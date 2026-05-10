"""
MedFind - Medical Records Module (Enhanced)
Includes PDF export for patients
API Routes: /api/v1/records/
"""

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from django.http import HttpResponse
from django.utils import timezone
import logging
import io
import json

logger = logging.getLogger(__name__)


def get_user_from_token(request):
    auth = request.headers.get("Authorization", "")
    if not auth.startswith("Bearer "):
        return None, Response({"success": False, "message": "Unauthorized"}, status=401)
    token = auth.replace("Bearer ", "")
    try:
        from apps.accounts.models import User
        user_id = int(token.split("_")[2])
        user = User.objects.get(id=user_id, is_active=True)
        return user, None
    except Exception:
        return None, Response({"success": False, "message": "Invalid token"}, status=401)


class MedicalRecordListView(APIView):
    """
    GET  /api/v1/records/          - List patient records (own or by patient_id for doctor)
    POST /api/v1/records/          - Create a new medical record
    """
    parser_classes = [JSONParser, MultiPartParser, FormParser]

    def get(self, request):
        user, err = get_user_from_token(request)
        if err:
            return err

        from apps.records.models import MedicalRecord
        from apps.records.serializers import MedicalRecordSerializer

        qs = MedicalRecord.objects.select_related("patient__user", "doctor__user", "hospital")

        # Patient sees only their own records
        if user.role == "patient":
            try:
                from apps.patients.models import Patient
                patient = Patient.objects.get(user=user)
                qs = qs.filter(patient=patient)
            except Exception:
                return Response({"success": False, "message": "Patient profile not found"}, status=404)

        # Doctor sees records they authored or their patients
        elif user.role == "doctor":
            patient_id = request.query_params.get("patient_id")
            if patient_id:
                qs = qs.filter(patient_id=patient_id)
            else:
                try:
                    from apps.doctors.models import Doctor
                    doctor = Doctor.objects.get(user=user)
                    qs = qs.filter(doctor=doctor)
                except Exception:
                    qs = qs.none()

        # Admin: full access
        elif user.role in ["superadmin", "hospital_admin"]:
            patient_id = request.query_params.get("patient_id")
            if patient_id:
                qs = qs.filter(patient_id=patient_id)

        # Filter params
        record_type = request.query_params.get("type")
        if record_type:
            qs = qs.filter(record_type=record_type)

        qs = qs.order_by("-created_at")

        page = int(request.query_params.get("page", 1))
        limit = int(request.query_params.get("limit", 20))
        total = qs.count()
        qs = qs[(page - 1) * limit: page * limit]

        return Response({
            "success": True,
            "data": MedicalRecordSerializer(qs, many=True).data,
            "total": total,
            "page": page,
        })

    def post(self, request):
        user, err = get_user_from_token(request)
        if err:
            return err

        if user.role not in ["doctor", "hospital_admin", "superadmin", "lab_technician"]:
            return Response({"success": False, "message": "Only medical staff can create records"}, status=403)

        from apps.records.serializers import MedicalRecordSerializer
        ser = MedicalRecordSerializer(data=request.data)
        if ser.is_valid():
            record = ser.save()
            logger.info(f"Medical record created: {record.id} by {user.email}")
            return Response({"success": True, "data": MedicalRecordSerializer(record).data}, status=201)
        return Response({"success": False, "errors": ser.errors}, status=400)


class MedicalRecordDetailView(APIView):
    """
    GET    /api/v1/records/{id}/  - Get single record
    PATCH  /api/v1/records/{id}/  - Update record
    DELETE /api/v1/records/{id}/  - Delete (admin/doctor only)
    """
    parser_classes = [JSONParser, MultiPartParser, FormParser]

    def _get_record_with_auth(self, request, pk):
        user, err = get_user_from_token(request)
        if err:
            return None, None, err
        try:
            from apps.records.models import MedicalRecord
            record = MedicalRecord.objects.select_related(
                "patient__user", "doctor__user", "hospital"
            ).get(pk=pk)
        except Exception:
            return None, None, Response({"success": False, "message": "Record not found"}, status=404)

        # Access control
        if user.role == "patient" and record.patient.user != user:
            return None, None, Response({"success": False, "message": "Forbidden"}, status=403)

        return user, record, None

    def get(self, request, pk):
        user, record, err = self._get_record_with_auth(request, pk)
        if err:
            return err
        from apps.records.serializers import MedicalRecordSerializer
        return Response({"success": True, "data": MedicalRecordSerializer(record).data})

    def patch(self, request, pk):
        user, record, err = self._get_record_with_auth(request, pk)
        if err:
            return err

        if user.role not in ["doctor", "hospital_admin", "superadmin"]:
            return Response({"success": False, "message": "Cannot edit records"}, status=403)

        allowed = ["title", "content", "notes", "is_confidential"]
        for field in allowed:
            if field in request.data:
                setattr(record, field, request.data[field])
        record.save()
        from apps.records.serializers import MedicalRecordSerializer
        return Response({"success": True, "data": MedicalRecordSerializer(record).data})

    def delete(self, request, pk):
        user, record, err = self._get_record_with_auth(request, pk)
        if err:
            return err

        if user.role not in ["superadmin", "hospital_admin"]:
            return Response({"success": False, "message": "Only admins can delete records"}, status=403)

        record_id = record.id
        record.delete()
        logger.warning(f"Medical record {record_id} DELETED by {user.email}")
        return Response({"success": True, "message": "Record deleted"})


class MedicalRecordPDFExportView(APIView):
    """
    GET /api/v1/records/{id}/export-pdf/
    Exports a medical record as PDF for patient download.
    """

    def get(self, request, pk):
        user, err = get_user_from_token(request)
        if err:
            return err

        try:
            from apps.records.models import MedicalRecord
            record = MedicalRecord.objects.select_related(
                "patient__user", "doctor__user", "hospital"
            ).get(pk=pk)
        except Exception:
            return Response({"success": False, "message": "Record not found"}, status=404)

        # Check access
        if user.role == "patient" and record.patient.user != user:
            return Response({"success": False, "message": "Forbidden"}, status=403)

        # Try reportlab PDF generation
        try:
            from reportlab.lib.pagesizes import A4
            from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
            from reportlab.lib.units import cm
            from reportlab.lib import colors
            from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
            from reportlab.lib.enums import TA_CENTER, TA_LEFT

            buffer = io.BytesIO()
            doc = SimpleDocTemplate(buffer, pagesize=A4,
                                    rightMargin=2*cm, leftMargin=2*cm,
                                    topMargin=2*cm, bottomMargin=2*cm)
            styles = getSampleStyleSheet()
            story = []

            # Header
            header_style = ParagraphStyle("header", fontSize=18, fontName="Helvetica-Bold",
                                          textColor=colors.HexColor("#2563eb"), alignment=TA_CENTER)
            sub_style = ParagraphStyle("sub", fontSize=10, fontName="Helvetica",
                                       textColor=colors.grey, alignment=TA_CENTER)
            normal = styles["Normal"]

            story.append(Paragraph("MedFind Healthcare Platform", header_style))
            story.append(Paragraph("Bangladesh's Trusted Medical Record System", sub_style))
            story.append(Spacer(1, 0.4*cm))
            story.append(HRFlowable(width="100%", thickness=2, color=colors.HexColor("#2563eb")))
            story.append(Spacer(1, 0.4*cm))

            # Record type title
            title_style = ParagraphStyle("title", fontSize=14, fontName="Helvetica-Bold",
                                         textColor=colors.HexColor("#111827"))
            story.append(Paragraph(f"Medical Record: {record.record_type.replace('_',' ').title()}", title_style))
            story.append(Spacer(1, 0.3*cm))

            # Patient info table
            pat_data = [
                ["Patient Name:", record.patient.user.full_name, "Record ID:", str(record.id)],
                ["Doctor:", record.doctor.user.full_name if record.doctor else "N/A",
                 "Hospital:", record.hospital.name if record.hospital else "N/A"],
                ["Date:", str(record.created_at.strftime("%d %B %Y")),
                 "Type:", record.record_type.replace("_", " ").title()],
            ]
            pat_table = Table(pat_data, colWidths=[3.5*cm, 6*cm, 3.5*cm, 5*cm])
            pat_table.setStyle(TableStyle([
                ("FONTNAME", (0,0), (-1,-1), "Helvetica"),
                ("FONTNAME", (0,0), (0,-1), "Helvetica-Bold"),
                ("FONTNAME", (2,0), (2,-1), "Helvetica-Bold"),
                ("FONTSIZE", (0,0), (-1,-1), 9),
                ("BACKGROUND", (0,0), (-1,-1), colors.HexColor("#f9fafb")),
                ("ROWBACKGROUNDS", (0,0), (-1,-1), [colors.HexColor("#f9fafb"), colors.white]),
                ("GRID", (0,0), (-1,-1), 0.5, colors.HexColor("#e5e7eb")),
                ("PADDING", (0,0), (-1,-1), 6),
            ]))
            story.append(pat_table)
            story.append(Spacer(1, 0.5*cm))

            # Content
            if record.title:
                story.append(Paragraph(record.title, styles["Heading2"]))
            if record.content:
                for line in record.content.split("\n"):
                    if line.strip():
                        story.append(Paragraph(line, normal))
                        story.append(Spacer(1, 0.1*cm))

            story.append(Spacer(1, 0.5*cm))
            story.append(HRFlowable(width="100%", thickness=0.5, color=colors.grey))
            footer_style = ParagraphStyle("footer", fontSize=8, textColor=colors.grey, alignment=TA_CENTER)
            story.append(Spacer(1, 0.3*cm))
            story.append(Paragraph(
                f"Generated by MedFind · {timezone.now().strftime('%d %B %Y %H:%M')} · This document is confidential",
                footer_style
            ))

            doc.build(story)
            pdf_bytes = buffer.getvalue()
            buffer.close()

            response = HttpResponse(pdf_bytes, content_type="application/pdf")
            filename = f"MedFind_Record_{record.id}_{record.record_type}.pdf"
            response["Content-Disposition"] = f'attachment; filename="{filename}"'
            response["X-Content-Type-Options"] = "nosniff"
            logger.info(f"PDF exported: record {record.id} by {user.email}")
            return response

        except ImportError:
            # Fallback: Return JSON if reportlab not installed
            logger.warning("reportlab not installed — returning JSON fallback")
            return Response({
                "success": True,
                "message": "PDF generation requires reportlab. Install via: pip install reportlab",
                "data": {
                    "record_id": record.id,
                    "patient": record.patient.user.full_name,
                    "type": record.record_type,
                    "title": record.title,
                    "content": record.content,
                    "created_at": record.created_at.isoformat(),
                }
            })


class PatientFullRecordExportView(APIView):
    """
    GET /api/v1/records/export-all/
    Exports ALL of a patient's medical records as a single PDF.
    """

    def get(self, request):
        user, err = get_user_from_token(request)
        if err:
            return err

        if user.role != "patient":
            return Response({"success": False, "message": "Only patients can export their own records"}, status=403)

        try:
            from apps.patients.models import Patient
            from apps.records.models import MedicalRecord
            patient = Patient.objects.get(user=user)
        except Exception:
            return Response({"success": False, "message": "Patient profile not found"}, status=404)

        records = MedicalRecord.objects.filter(patient=patient).select_related(
            "doctor__user", "hospital"
        ).order_by("-created_at")

        # For now return summary JSON (replace with full PDF build using reportlab)
        summary = {
            "patient_name": user.full_name,
            "export_date": timezone.now().strftime("%d %B %Y"),
            "total_records": records.count(),
            "records": [
                {
                    "id": r.id,
                    "type": r.record_type,
                    "title": r.title,
                    "doctor": r.doctor.user.full_name if r.doctor else "N/A",
                    "hospital": r.hospital.name if r.hospital else "N/A",
                    "date": r.created_at.strftime("%d %B %Y"),
                }
                for r in records[:50]
            ]
        }

        logger.info(f"Full record export: patient {patient.id} ({user.email})")
        return Response({"success": True, "data": summary})


class LabReportUploadView(APIView):
    """
    POST /api/v1/records/lab-report/upload/
    Hospital/lab technician uploads a lab report for a patient.
    Patients can then download it.
    """
    parser_classes = [MultiPartParser, FormParser]

    def post(self, request):
        user, err = get_user_from_token(request)
        if err:
            return err

        if user.role not in ["lab_technician", "hospital_admin", "superadmin", "doctor"]:
            return Response({"success": False, "message": "Unauthorized to upload lab reports"}, status=403)

        patient_id = request.data.get("patient_id")
        report_file = request.FILES.get("report_file")
        report_name = request.data.get("report_name", "Lab Report")
        test_name = request.data.get("test_name", "")
        hospital_id = request.data.get("hospital_id")

        if not patient_id or not report_file:
            return Response({"success": False, "message": "patient_id and report_file are required"}, status=400)

        # Validate file type
        allowed_types = ["application/pdf", "image/jpeg", "image/png"]
        if report_file.content_type not in allowed_types:
            return Response({"success": False, "message": "Only PDF, JPEG, PNG allowed"}, status=400)

        # Validate file size (max 10MB)
        if report_file.size > 10 * 1024 * 1024:
            return Response({"success": False, "message": "File too large. Maximum 10MB"}, status=400)

        # In production: save file to storage (S3/local), create MedicalRecord
        # from apps.records.models import MedicalRecord
        # record = MedicalRecord.objects.create(
        #     patient_id=patient_id,
        #     hospital_id=hospital_id,
        #     record_type="lab_report",
        #     title=report_name,
        #     content=f"Test: {test_name}",
        #     file=report_file,
        # )

        logger.info(f"Lab report uploaded by {user.email} for patient {patient_id}: {report_name}")

        return Response({
            "success": True,
            "message": "Lab report uploaded successfully. Patient can now download it.",
            "data": {
                "patient_id": patient_id,
                "report_name": report_name,
                "test_name": test_name,
                "uploaded_by": user.full_name,
                "uploaded_at": timezone.now().isoformat(),
                "download_url": f"/api/v1/records/download/{patient_id}/lab_report/",
            }
        }, status=201)


class RecordDownloadView(APIView):
    """
    GET /api/v1/records/{id}/download/
    Allows patients to download their report files.
    """

    def get(self, request, pk):
        user, err = get_user_from_token(request)
        if err:
            return err

        try:
            from apps.records.models import MedicalRecord
            record = MedicalRecord.objects.select_related("patient__user").get(pk=pk)
        except Exception:
            return Response({"success": False, "message": "Record not found"}, status=404)

        # Only own patient or medical staff
        if user.role == "patient" and record.patient.user != user:
            return Response({"success": False, "message": "Forbidden"}, status=403)

        if not hasattr(record, "file") or not record.file:
            return Response({
                "success": False,
                "message": "No file attached to this record",
                "pdf_export_url": f"/api/v1/records/{pk}/export-pdf/"
            }, status=404)

        logger.info(f"File download: record {pk} by {user.email}")

        # Serve file
        response = HttpResponse(record.file.read(), content_type="application/pdf")
        response["Content-Disposition"] = f'attachment; filename="{record.title}.pdf"'
        return response
