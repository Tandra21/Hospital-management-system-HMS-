# medfind/ai/views.py
import uuid, json, logging
from django.http import JsonResponse
from django.views import View
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from django.utils import timezone
from .models import ChatSession, ChatMessage, HealthRecord
from .utils import call_claude, extract_metadata, detect_emergency

logger = logging.getLogger(__name__)

@method_decorator(csrf_exempt, name='dispatch')
class AIChatView(View):
    def post(self, request):
        try:
            body    = json.loads(request.body)
            message = body.get('message','').strip()
            if not message:
                return JsonResponse({'error':'Message required'}, status=400)

            sid = body.get('session_id') or request.session.get('ai_sid')
            if not sid:
                sid = str(uuid.uuid4())

            session, _ = ChatSession.objects.get_or_create(
                session_id=sid,
                defaults={
                    'user_ip': self._ip(request),
                    'user_id': str(request.user.id) if request.user.is_authenticated else None,
                }
            )
            request.session['ai_sid'] = sid

            recent = list(ChatMessage.objects.filter(session=session).order_by('-created_at')[:20])
            history = [{'role':m.role,'content':m.content} for m in reversed(recent)]
            history.append({'role':'user','content':message})

            ChatMessage.objects.create(session=session, role='user', content=message,
                                       is_emergency=detect_emergency(message))

            reply = call_claude(history)
            meta  = extract_metadata(reply)

            ChatMessage.objects.create(session=session, role='assistant', content=reply,
                                       urgency=meta['urgency'], specialist=meta['specialist'],
                                       is_emergency=meta['is_emergency'])
            session.turn_count += 1
            session.save()

            return JsonResponse({'response':reply, 'session_id':sid,
                                 'is_emergency':meta['is_emergency'],
                                 'urgency':meta['urgency'],
                                 'specialist':meta['specialist'],
                                 'disclaimer':'⚠️ AI suggestions are supportive only. Always consult a qualified doctor before making any medical decisions.'})
        except Exception as e:
            logger.error(f'AIChatView error: {e}', exc_info=True)
            return JsonResponse({'error':'AI service error'}, status=500)

    def _ip(self, r):
        x = r.META.get('HTTP_X_FORWARDED_FOR')
        return x.split(',')[0].strip() if x else r.META.get('REMOTE_ADDR')


@method_decorator(csrf_exempt, name='dispatch')
class SymptomAnalyzeView(View):
    def post(self, request):
        try:
            body     = json.loads(request.body)
            symptoms = body.get('symptoms', [])
            if not symptoms:
                return JsonResponse({'error':'Symptoms required'}, status=400)

            prompt = (
                f"Patient symptoms: {', '.join(symptoms)}\n"
                "Respond ONLY with valid JSON (no markdown):\n"
                '{"conditions":[{"name":"...","prob":75,"color":"#22d3ee"}],'
                '"urgency":"Mild","urgencyClass":"s","specialist":"...","action":"..."}'
            )
            import anthropic
            client = anthropic.Anthropic(api_key=settings.ANTHROPIC_API_KEY)
            resp = client.messages.create(
                model=settings.ANTHROPIC_MODEL,
                max_tokens=600,
                system='Medical AI. Respond ONLY with valid JSON.',
                messages=[{'role':'user','content':prompt}]
            )
            raw    = resp.content[0].text.replace('```json','').replace('```','').strip()
            result = json.loads(raw)
            return JsonResponse(result)
        except Exception as e:
            return JsonResponse({'error':str(e)}, status=500)


class ChatHistoryView(View):
    def get(self, request):
        sid = request.GET.get('session_id')
        if not sid:
            return JsonResponse({'error':'session_id required'}, status=400)
        try:
            session = ChatSession.objects.get(session_id=sid)
            msgs    = ChatMessage.objects.filter(session=session).order_by('created_at')
            return JsonResponse({
                'session_id':  sid,
                'turn_count':  session.turn_count,
                'messages': [{
                    'role':         m.role,
                    'content':      m.content,
                    'created_at':   m.created_at.isoformat(),
                    'urgency':      m.urgency,
                    'specialist':   m.specialist,
                    'is_emergency': m.is_emergency,
                } for m in msgs]
            })
        except ChatSession.DoesNotExist:
            return JsonResponse({'error':'Session not found'}, status=404)


@method_decorator(csrf_exempt, name='dispatch')
class HealthRecordView(View):
    def post(self, request):
        try:
            body = json.loads(request.body)
            HealthRecord.objects.create(
                user_id   = body.get('user_id','anonymous'),
                bmi       = body.get('bmi'),
                systolic  = body.get('systolic'),
                diastolic = body.get('diastolic'),
                sugar     = body.get('sugar'),
                weight    = body.get('weight'),
                notes     = body.get('notes',''),
            )
            return JsonResponse({'status':'saved'})
        except Exception as e:
            return JsonResponse({'error':str(e)}, status=500)

    def get(self, request):
        uid  = request.GET.get('user_id','anonymous')
        recs = HealthRecord.objects.filter(user_id=uid).order_by('-created_at')[:30]
        return JsonResponse({'records':[{
            'bmi':r.bmi,'systolic':r.systolic,'diastolic':r.diastolic,
            'sugar':r.sugar,'weight':r.weight,'notes':r.notes,
            'created_at':r.created_at.isoformat()
        } for r in recs]})
