/**
 * MEDFIND API Integration
 * Utility functions for connecting frontend to Django backend
 */

const API_CONFIG = {
    BASE_URL: 'http://localhost:8000/api',
    TIMEOUT: 10000, // 10 seconds
};

class MedFindAPI {
    constructor(baseUrl = API_CONFIG.BASE_URL) {
        this.baseUrl = baseUrl;
        this.timeout = API_CONFIG.TIMEOUT;
    }

    /**
     * Make API request with error handling
     */
    async request(endpoint, method = 'GET', data = null) {
        const url = `${this.baseUrl}${endpoint}`;
        
        const options = {
            method: method,
            headers: {
                'Content-Type': 'application/json',
                'Accept': 'application/json',
            },
        };

        if (data && (method === 'POST' || method === 'PUT' || method === 'PATCH')) {
            options.body = JSON.stringify(data);
        }

        try {
            const response = await Promise.race([
                fetch(url, options),
                new Promise((_, reject) => 
                    setTimeout(() => reject(new Error('API request timeout')), this.timeout)
                )
            ]);

            if (!response.ok) {
                const error = await response.json();
                throw new Error(error.error || `API Error: ${response.status}`);
            }

            return await response.json();
        } catch (error) {
            console.error('API Error:', error);
            throw error;
        }
    }

    // ===== Hospital APIs =====

    async getHospitals(filters = {}) {
        let endpoint = '/hospitals/';
        const params = new URLSearchParams();
        
        if (filters.city) params.append('city', filters.city);
        if (filters.specialty) params.append('specialty', filters.specialty);
        if (filters.search) params.append('search', filters.search);
        
        if (params.toString()) {
            endpoint += `?${params.toString()}`;
        }
        
        return this.request(endpoint);
    }

    async getHospital(id) {
        return this.request(`/hospitals/${id}/`);
    }

    async createHospital(data) {
        return this.request('/hospitals/', 'POST', data);
    }

    async updateHospital(id, data) {
        return this.request(`/hospitals/${id}/`, 'PUT', data);
    }

    async getHospitalDoctors(hospitalId) {
        return this.request(`/hospitals/${hospitalId}/doctors/`);
    }

    async getHospitalServices(hospitalId) {
        return this.request(`/hospitals/${hospitalId}/services/`);
    }

    // ===== Doctor APIs =====

    async getDoctors(filters = {}) {
        let endpoint = '/doctors/';
        const params = new URLSearchParams();
        
        if (filters.specialization) params.append('specialization', filters.specialization);
        if (filters.hospital_id) params.append('hospital_id', filters.hospital_id);
        if (filters.search) params.append('search', filters.search);
        
        if (params.toString()) {
            endpoint += `?${params.toString()}`;
        }
        
        return this.request(endpoint);
    }

    async getDoctor(id) {
        return this.request(`/doctors/${id}/`);
    }

    async createDoctor(data) {
        return this.request('/doctors/', 'POST', data);
    }

    async updateDoctor(id, data) {
        return this.request(`/doctors/${id}/`, 'PUT', data);
    }

    async getDoctorAvailability(doctorId) {
        return this.request(`/doctors/${doctorId}/availability/`);
    }

    // ===== Patient APIs =====

    async getPatients() {
        return this.request('/patients/');
    }

    async getPatient(id) {
        return this.request(`/patients/${id}/`);
    }

    async createPatient(data) {
        return this.request('/patients/', 'POST', data);
    }

    async updatePatient(id, data) {
        return this.request(`/patients/${id}/`, 'PUT', data);
    }

    async getPatientMedicalHistory(patientId) {
        return this.request(`/patients/${patientId}/medical_history/`);
    }

    async getPatientAppointments(patientId) {
        return this.request(`/patients/${patientId}/appointments/`);
    }

    // ===== Appointment APIs =====

    async getAppointments() {
        return this.request('/appointments/');
    }

    async getAppointment(id) {
        return this.request(`/appointments/${id}/`);
    }

    async createAppointment(data) {
        return this.request('/appointments/', 'POST', data);
    }

    async updateAppointment(id, data) {
        return this.request(`/appointments/${id}/`, 'PUT', data);
    }

    async getAppointmentsByPatient(patientId) {
        return this.request(`/appointments/by_patient/?patient_id=${patientId}`);
    }

    async getAppointmentsByDoctor(doctorId) {
        return this.request(`/appointments/by_doctor/?doctor_id=${doctorId}`);
    }

    // ===== Lab Test APIs =====

    async getLabTests() {
        return this.request('/lab-tests/');
    }

    async getLabTest(id) {
        return this.request(`/lab-tests/${id}/`);
    }

    async createLabTest(data) {
        return this.request('/lab-tests/', 'POST', data);
    }

    async updateLabTest(id, data) {
        return this.request(`/lab-tests/${id}/`, 'PUT', data);
    }

    async getLabTestsByPatient(patientId) {
        return this.request(`/lab-tests/by_patient/?patient_id=${patientId}`);
    }

    // ===== Billing APIs =====

    async getBillings() {
        return this.request('/billing/');
    }

    async getBilling(id) {
        return this.request(`/billing/${id}/`);
    }

    async createBilling(data) {
        return this.request('/billing/', 'POST', data);
    }

    async updateBilling(id, data) {
        return this.request(`/billing/${id}/`, 'PUT', data);
    }

    async getBillingsByPatient(patientId) {
        return this.request(`/billing/by_patient/?patient_id=${patientId}`);
    }

    async markBillingAsPaid(billingId) {
        return this.request(`/billing/${billingId}/mark_as_paid/`, 'POST');
    }

    // ===== Pharmacy APIs =====

    async getPharmacy() {
        return this.request('/pharmacy/');
    }

    async getPharmacyItem(id) {
        return this.request(`/pharmacy/${id}/`);
    }

    async createPharmacyItem(data) {
        return this.request('/pharmacy/', 'POST', data);
    }

    async updatePharmacyItem(id, data) {
        return this.request(`/pharmacy/${id}/`, 'PUT', data);
    }

    // ===== Medical History APIs =====

    async getMedicalHistory() {
        return this.request('/medical-history/');
    }

    async getMedicalHistoryRecord(id) {
        return this.request(`/medical-history/${id}/`);
    }

    async createMedicalHistory(data) {
        return this.request('/medical-history/', 'POST', data);
    }

    async updateMedicalHistory(id, data) {
        return this.request(`/medical-history/${id}/`, 'PUT', data);
    }

    // ===== Utility Methods =====

    /**
     * Test API Connection
     */
    async testConnection() {
        try {
            const response = await this.request('/hospitals/?page_size=1');
            return { success: true, message: 'API is connected' };
        } catch (error) {
            return { success: false, message: error.message };
        }
    }

    /**
     * Format API errors for display
     */
    formatError(error) {
        if (typeof error === 'string') {
            return error;
        }
        if (error.message) {
            return error.message;
        }
        return 'An unknown error occurred';
    }
}

// Create global instance
const api = new MedFindAPI();

// Test connection on load
document.addEventListener('DOMContentLoaded', async function() {
    const connectionStatus = await api.testConnection();
    if (!connectionStatus.success) {
        console.warn('⚠️ Backend API Connection Failed:', connectionStatus.message);
    } else {
        console.log('✅ Backend API Connected Successfully');
    }
});

// Export for use in other scripts
if (typeof module !== 'undefined' && module.exports) {
    module.exports = MedFindAPI;
}
