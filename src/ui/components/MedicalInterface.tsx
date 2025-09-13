"use client";

console.log("🧠 MedicalInterface component mounted");

import { useNavigate } from "react-router-dom";
import React, { useState, useRef } from "react";
import axios from "axios";
import { Upload, FileText, Download, X } from "lucide-react";
import { Header } from "./header";
import { PatientSidebar } from "./patient-sidebar";

interface PatientInfo {
  name: string;
  id: string;
  dob: string;
  phone: string;
  email: string;
  address: string;
}

export default function MedicalInterface() {
  const [file, setFile] = useState<File | null>(null);
  const [isDragging, setIsDragging] = useState(false);
  const [isUploading, setIsUploading] = useState(false);
  const [progress, setProgress] = useState(0);
  const [progressText, setProgressText] = useState("");
  const navigate = useNavigate();
  const isNavigatingRef = useRef(false);

  const patientInfo: PatientInfo = {
    name: "John Smith",
    id: "PT-2024-001",
    dob: "March 15, 1985",
    phone: "+1 (555) 123-4567",
    email: "john.smith@email.com",
    address: "123 Main St, City, State",
  };

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(true);
  };

  const handleDragLeave = () => setIsDragging(false);

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
    const dropped = e.dataTransfer.files?.[0];
    if (dropped && dropped.name.endsWith(".nii.gz")) {
      setFile(dropped);
    } else {
      alert("❌ Please upload a valid .nii.gz file");
    }
  };

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    const selected = e.target.files?.[0];
    if (selected && selected.name.endsWith(".nii.gz")) {
      setFile(selected);
    } else {
      alert("❌ Only .nii.gz files are supported.");
    }
  };

  const formatFileSize = (bytes: number) => {
    if (bytes === 0) return "0 Bytes";
    const k = 1024;
    const sizes = ["Bytes", "KB", "MB", "GB"];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return Number.parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + " " + sizes[i];
  };

  const processFile = async () => {

    if (!file) {
      alert("No file selected.");
      return;
    }

    setIsUploading(true);
    setProgress(0);
    setProgressText("Starting...");

    // Reset navigation flag for a new upload
    isNavigatingRef.current = false;

    try {
      const formData = new FormData();
      formData.append("file", file);

      // Use relative paths for API calls. Vercel will route them to the backend.
      const apiUrl = "/api";

      const response = await axios.post(`${apiUrl}/process-nifti`, formData, {
        headers: { "Content-Type": "multipart/form-data" },
      });

      console.log("Upload complete:", response.data);
      const { file_id } = response.data;
      console.log("File ID received:", file_id);

      // Use a safer, recursive setTimeout pattern for polling
      const poll = async () => {
        try {
          const res = await axios.get(`${apiUrl}/progress/${file_id}`);
          const { progress, step, filename } = res.data;

          // Check if the backend is reporting a processing error in the 'step' message
          if (typeof step === 'string' && (step.toLowerCase().includes('error') || step.toLowerCase().includes('failed'))) {
            setProgressText(step);
            alert(`❌ Processing failed on the server: ${step}`);
            setIsUploading(false);
            return; // Stop polling on error
          }

          console.log("Progress update:", progress, step, filename);
          setProgress(progress);
          setProgressText(step);

          if (progress >= 100 && filename) {
            setIsUploading(false); // Stop showing the progress bar
            navigate(`/viewer?file=${encodeURIComponent(filename)}`); // Navigate with a shareable URL
            return; // Stop polling on success
          }

          if (progress >= 100 && !filename) {
            console.warn("Processing complete but STL filename missing. Retrying...");
          }

          // If not complete, schedule the next poll
          setTimeout(poll, 500); // Poll every 500ms
        } catch (err) {
          console.error("Polling error:", err);
          alert("❌ Failed to fetch progress.");
          setIsUploading(false);
        }
      };

      // Start the first poll
      setTimeout(poll, 500);

    } catch (err: any) {
      console.error("Upload error:", err);
      if (err.code === 'ERR_NETWORK') {
        alert(`❌ Network Error: Could not connect to the server. Please ensure the backend service is running and accessible.`);
      } else {
        alert(`❌ ${err.response?.data?.detail || err.message || 'An unknown error occurred during upload.'}`);
      }
      setIsUploading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-blue-50">
      {/* Header */}
      <Header />

      <div className="flex">
        {/* Sidebar */}
        <PatientSidebar patientInfo={patientInfo} />

        {/* Upload Area */}
        <div className="flex-1 p-8">
          <div className="max-w-4xl mx-auto">
            <h2 className="text-2xl font-bold text-slate-900 mb-2">CT Scan Upload</h2>
            <p className="text-slate-600 mb-6">Upload a NIfTI (.nii.gz) file</p>

            <div
              className={`relative border-2 border-dashed rounded-xl p-12 text-center transition-all duration-200 ${
                isDragging
                  ? "border-blue-400 bg-blue-50"
                  : "border-slate-300 bg-white hover:border-blue-300 hover:bg-slate-50"
              }`}
              onDragOver={handleDragOver}
              onDragLeave={handleDragLeave}
              onDrop={handleDrop}
              onClick={() => document.getElementById("file-upload")?.click()}
            >
              <div className="flex flex-col items-center space-y-4">
                <div
                  className={`w-16 h-16 rounded-full flex items-center justify-center ${
                    isDragging ? "bg-blue-100" : "bg-slate-100"
                  }`}
                >
                  <Upload className={`w-8 h-8 ${isDragging ? "text-blue-600" : "text-slate-600"}`} />
                </div>
                <div>
                  <h3 className="text-xl font-semibold text-slate-900 mb-2">Upload NIfTI File</h3>
                  <p className="text-slate-600 mb-4">Drag & drop or click to browse</p>
                  <p className="text-sm text-slate-500">Only one .nii.gz file allowed</p>
                </div>
                <button className="px-6 py-3 bg-blue-600 text-white rounded-lg font-medium hover:bg-blue-700 transition-colors">
                  Choose File
                </button>
              </div>
              <input
                type="file"
                className="hidden"
                id="file-upload"
                onChange={handleFileSelect}
                accept=".nii.gz"
              />
            </div>

            {file && (
              <div className="mt-8">
                <div className="flex items-center justify-between mb-4">
                  <h3 className="text-lg font-semibold text-slate-900">Selected File</h3>
                  <button
                    onClick={() => {
                      console.log("🚀 Button clicked");
                      processFile();
                    }}
                    disabled={isUploading}
                    className="flex items-center space-x-2 px-4 py-2 bg-green-600 text-white rounded-lg font-medium hover:bg-green-700 disabled:bg-green-400"
                  >
                    {isUploading ? (
                      <>
                        <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin mr-2"></div>
                        <span>Processing...</span>
                      </>
                    ) : (
                      <>
                        <Download className="w-4 h-4" />
                        <span>Process</span>
                      </>
                    )}
                  </button>
                </div>

                <div className="bg-white rounded-lg shadow-sm border border-slate-200">
                  <div className="flex items-center justify-between p-4">
                    <div className="flex items-center space-x-3">
                      <div className="w-10 h-10 bg-blue-100 rounded-lg flex items-center justify-center">
                        <FileText className="w-5 h-5 text-blue-600" />
                      </div>
                      <div>
                        <p className="font-medium text-slate-900">{file.name}</p>
                        <p className="text-sm text-slate-500">{formatFileSize(file.size)}</p>
                      </div>
                    </div>
                    <button
                      onClick={() => setFile(null)}
                      className="w-8 h-8 bg-red-100 text-red-600 rounded-full flex items-center justify-center hover:bg-red-200 transition-colors"
                    >
                      <X className="w-4 h-4" />
                    </button>
                  </div>
                </div>

                {isUploading && (
                  <div className="mt-4">
                    <div className="text-slate-700 mb-1 text-sm">Processing: {progressText}</div>
                    <div className="w-full bg-slate-200 rounded-full h-4 overflow-hidden">
                      <div
                        className="bg-blue-600 h-full transition-all duration-300"
                        style={{ width: `${progress}%` }}
                      />
                    </div>
                    <p className="text-sm text-slate-500 mt-1">{progress}%</p>
                  </div>
                )}
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
