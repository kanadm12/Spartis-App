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
export declare function PatientSidebar({ patientInfo }: PatientSidebarProps): import("react/jsx-runtime").JSX.Element;
export {};
