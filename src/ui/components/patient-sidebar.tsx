import { User, Calendar, Phone, Mail, MapPin } from "lucide-react";

interface PatientInfo {
  name: string;
  id: string;
  dob: string;
  phone: string;
  email: string;
  address: string;
}

interface PatientSidebarProps {
  patientInfo: PatientInfo;
}

export function PatientSidebar({ patientInfo }: PatientSidebarProps) {
  return (
    <div className="w-80 bg-white shadow-lg h-[calc(100vh-80px)] overflow-y-auto">
      <div className="p-6">
        <div className="flex items-center space-x-3 mb-6">
          <div className="w-10 h-10 bg-blue-100 rounded-full flex items-center justify-center">
            <User className="w-5 h-5 text-blue-600" />
          </div>
          <h2 className="text-lg font-semibold text-slate-900">Patient Details</h2>
        </div>

        <div className="space-y-4">
          <div className="bg-slate-50 rounded-lg p-4">
            <div className="flex items-center space-x-2 mb-3">
              <User className="w-4 h-4 text-slate-600" />
              <span className="text-sm font-medium text-slate-600">Patient Name</span>
            </div>
            <p className="text-slate-900 font-medium">{patientInfo.name}</p>
            <p className="text-sm text-slate-500">ID: {patientInfo.id}</p>
          </div>

          <div className="bg-slate-50 rounded-lg p-4">
            <div className="flex items-center space-x-2 mb-3">
              <Calendar className="w-4 h-4 text-slate-600" />
              <span className="text-sm font-medium text-slate-600">Date of Birth</span>
            </div>
            <p className="text-slate-900">{patientInfo.dob}</p>
          </div>

          <div className="bg-slate-50 rounded-lg p-4">
            <div className="flex items-center space-x-2 mb-3">
              <Phone className="w-4 h-4 text-slate-600" />
              <span className="text-sm font-medium text-slate-600">Phone</span>
            </div>
            <p className="text-slate-900">{patientInfo.phone}</p>
          </div>

          <div className="bg-slate-50 rounded-lg p-4">
            <div className="flex items-center space-x-2 mb-3">
              <Mail className="w-4 h-4 text-slate-600" />
              <span className="text-sm font-medium text-slate-600">Email</span>
            </div>
            <p className="text-slate-900 text-sm">{patientInfo.email}</p>
          </div>

          <div className="bg-slate-50 rounded-lg p-4">
            <div className="flex items-center space-x-2 mb-3">
              <MapPin className="w-4 h-4 text-slate-600" />
              <span className="text-sm font-medium text-slate-600">Address</span>
            </div>
            <p className="text-slate-900 text-sm">{patientInfo.address}</p>
          </div>
        </div>
      </div>
    </div>
  );
}