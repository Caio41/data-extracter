"use client";
import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { Upload, FileText, File, Table } from "lucide-react";
import ErrorModal from "@/components/ErrorModal";
import { Checkbox } from "@/components/ui/checkbox";

export default function Home() {
  const [file, setFile] = useState<File | null>(null);
  const [format, setFormat] = useState<"txt" | "docx" | "csv" | null>(null);
  const [isUploading, setIsUploading] = useState(false);
  const [downloadFile, setDownloadFile] = useState<Blob | null>(null);
  const [downloadFileName, setDownloadFileName] = useState<string>("");
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [isTable, setIsTable] = useState(false);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const acceptedFormats = isTable ? ["image/png", "image/jpeg"] : ["image/png", "image/jpeg", "application/pdf"];
    const selectedFile = e.target.files ? e.target.files[0] : null;

    if (selectedFile) {
      if (!acceptedFormats.includes(selectedFile.type)) {
        setErrorMessage("Formato de arquivo não aceito nesse modo. Por favor, selecione uma imagem" + (isTable ? "." : " ou PDF."));
        setFile(null);
        return;
      }

      setFile(selectedFile);
      setDownloadFile(null);
      setDownloadFileName("");
    }
  };

  const handleDownload = () => {
    if (!downloadFile || !downloadFileName) return;

    const url = window.URL.createObjectURL(downloadFile);
    const a = document.createElement("a");
    a.href = url;
    a.download = downloadFileName;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    window.URL.revokeObjectURL(url);
  };

  const handleUpload = async () => {
    if (!file || (!format && !isTable)) return;
    setIsUploading(true);
    setErrorMessage(null);

    const formData = new FormData();
    formData.append("arquivo", file);

    try {
      const apiBaseUrl = process.env.NEXT_PUBLIC_BACKEND_URL;
      const route = isTable ? "/tabelas/tesseract/" : `/documents/${format === "txt" ? "img-to-txt" : "img-to-doc"}`;

      const response = await fetch(apiBaseUrl + route, {
        method: "POST",
        body: formData,
      });
      console.log(response);

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || "Erro ao enviar o arquivo. Por favor, tente novamente.");
      }

      const contentDisposition = response.headers.get("content-disposition");
      let filename = `arquivo_convertido.${isTable ? "csv" : format}`;

      if (contentDisposition) {
        const match = contentDisposition.match(/filename\*?=(?:UTF-8'')?"?([^";]+)"?/i);
        if (match) {
          filename = decodeURIComponent(match[1]);
        }
      }

      const blob = await response.blob();
      setDownloadFile(blob);
      setDownloadFileName(filename);
    } catch (error: unknown) {
      console.error(error);
      setErrorMessage((error as Error).message || "Erro ao enviar o arquivo. Por favor, tente novamente.");
    } finally {
      setIsUploading(false);
    }
  };

  const closeErrorModal = () => {
    setErrorMessage(null);
  };

  return (
    <div className="flex flex-col items-center justify-center bg-gray-100 p-4">
      <Card className="w-full max-w-lg p-6 shadow-lg bg-white">
        <div className="flex flex-col items-center justify-center text-center space-y-4 py-4">
          <div className="flex items-center space-x-2 text-xl font-semibold text-gray-700">
            <span role="img" aria-label="light-bulb" className="text-yellow-500 text-2xl">💡</span>
            <span>Extraia texto a partir de imagens e documentos PDF</span>
          </div>
          <div className="text-gray-500 text-lg">
            Faça upload dos seus arquivos e deixe a tecnologia fazer o resto.
          </div>
        </div>

        <div className="text-center mb-4">
          <h1 className="text-xl font-semibold">Upload de arquivo</h1>
          {isTable && <p><span className="text-red-500">*</span>apenas imagens</p>}
        </div>
        <CardContent className="flex flex-col gap-4">
          <input type="file" accept={isTable ? "image/png, image/jpeg" : "image/png, image/jpeg, application/pdf"} onChange={handleFileChange} className="hidden" id="file-input" />
          <label htmlFor="file-input" className="cursor-pointer flex flex-col items-center border border-dashed border-gray-400 p-6 rounded-lg bg-gray-50 hover:bg-gray-100 transition">
            <Upload className="w-8 h-8 text-gray-600" />
            <span className="text-gray-700 mt-2">{file ? file.name : "Selecione um arquivo"}</span>
          </label>

          <div className="flex items-center gap-2">
            <Checkbox
              id="is-table"
              checked={isTable}
              onCheckedChange={(checked: boolean) => {
                setIsTable(!!checked);
                setFormat(checked ? "csv" : null);
                setDownloadFile(null);
                setDownloadFileName("");
              }}
            />
            <label htmlFor="is-table" className="text-gray-700 flex items-center gap-1">
              <Table className="w-4 h-4" />
              A imagem contém uma tabela
            </label>
          </div>

          {!isTable && (
            <>
              <h2 className="text-x font-semibold text-center mb-1">Selecione o formato de saída desejado</h2>
              <div className="flex gap-2 justify-center">
                <Button
                  variant={format === "txt" ? "default" : "outline"}
                  onClick={() => {
                    setFormat("txt");
                    setDownloadFile(null);
                    setDownloadFileName("");
                  }}
                >
                  <FileText className="w-4 h-4 mr-2" /> TXT
                </Button>
                <Button
                  variant={format === "docx" ? "default" : "outline"}
                  onClick={() => {
                    setFormat("docx");
                    setDownloadFile(null);
                    setDownloadFileName("");
                  }}
                >
                  <File className="w-4 h-4 mr-2" /> DOCX
                </Button>
              </div>
            </>
          )}

          <Button onClick={handleUpload} disabled={!file || (!format && !isTable) || isUploading}>
            {isUploading ? "Enviando..." : "Enviar"}
          </Button>

          {downloadFile && (
            <Button onClick={handleDownload} className="mt-2">
              Baixar arquivo
            </Button>
          )}
        </CardContent>
      </Card>

      {/* Modal de erro */}
      {errorMessage && <ErrorModal message={errorMessage} onClose={closeErrorModal} />}
    </div>
  );
}
