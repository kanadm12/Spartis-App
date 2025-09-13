import React, { useState } from "react"
import "./App.css"
import { Upload, Loader2, Eye, Download } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Card, CardContent } from "@/components/ui/card"
import STLViewer from "@/components/STLViewer"

function App() {
  const [file, setFile] = useState<File | null>(null)
  const [loading, setLoading] = useState(false)
  const [stlFile, setStlFile] = useState<string | null>(null)
  const [stlUrl, setStlUrl] = useState<string | null>(null)

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files?.[0]) {
      setFile(e.target.files[0])
    }
  }

  const handleUpload = async () => {
    if (!file) return
    setLoading(true)
    setStlFile(null)
    setStlUrl(null)

    const formData = new FormData()
    formData.append("file", file)

    try {
      const res = await fetch("http://localhost:8000/process-nifti/", {
        method: "POST",
        body: formData,
      })

      if (!res.ok) throw new Error("Upload failed")

      const data = await res.json()
      const filename = data.filename
      const url = `http://localhost:8000/outputs/${encodeURIComponent(filename)}`

      setStlFile(filename)
      setStlUrl(url)

      // Trigger file download automatically
      const link = document.createElement("a")
      link.href = url
      link.download = filename
      document.body.appendChild(link)
      link.click()
      document.body.removeChild(link)
    } catch (error) {
      alert("Something went wrong during upload or processing")
      console.error(error)
    } finally {
      setLoading(false)
    }
  }

  const handleViewMesh = async () => {
    if (!stlFile) return
    try {
      const res = await fetch(`http://localhost:8000/view-mesh/?filename=${encodeURIComponent(stlFile)}`)
      if (!res.ok) throw new Error("Viewer failed to launch")
      alert("Mesh viewer launched from backend")
    } catch (err) {
      alert("Failed to open mesh viewer")
      console.error(err)
    }
  }

  return (
    <main className="min-h-screen flex flex-col items-center justify-center bg-gradient-to-br from-slate-100 to-slate-300 p-4">
      <Card className="w-full max-w-md shadow-2xl border border-slate-200">
        <CardContent className="p-6 space-y-4">
          <h1 className="text-2xl font-semibold text-slate-800 text-center">NIfTI to Mesh</h1>
          <input
            type="file"
            accept=".nii.gz"
            onChange={handleFileChange}
            className="w-full"
          />
          <Button
            onClick={handleUpload}
            disabled={!file || loading}
            className="w-full flex items-center justify-center gap-2"
          >
            {loading ? <Loader2 className="animate-spin" /> : <Upload />}
            Upload & Process
          </Button>

          {stlFile && stlUrl && (
            <>
              <Button
                onClick={handleViewMesh}
                variant="outline"
                className="w-full flex items-center justify-center gap-2"
              >
                <Eye /> View Mesh (Backend)
              </Button>
              <a
                href={stlUrl}
                download={stlFile}
                className="w-full block text-center mt-2 text-blue-600 hover:underline"
              >
                <Download className="inline mr-1" /> Download STL
              </a>
              <p className="text-center text-sm text-slate-600">STL: {stlFile}</p>
            </>
          )}
        </CardContent>
      </Card>

      {stlUrl && (
        <div className="w-full max-w-4xl mt-10 shadow-lg">
          <STLViewer url={stlUrl} />
        </div>
      )}
    </main>
  )
}

export default App
