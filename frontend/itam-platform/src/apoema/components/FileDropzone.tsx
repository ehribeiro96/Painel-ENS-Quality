import { Paperclip, UploadCloud } from "lucide-react";
import type { ChangeEvent, DragEvent } from "react";

export function FileDropzone({
  onFiles,
  dragging,
  onDragStateChange,
  label = "Solte arquivos para anexar"
}: {
  onFiles: (files: File[]) => void;
  dragging: boolean;
  onDragStateChange: (dragging: boolean) => void;
  label?: string;
}) {
  function handleChange(event: ChangeEvent<HTMLInputElement>) {
    if (event.target.files) {
      onFiles(Array.from(event.target.files));
      event.target.value = "";
    }
  }

  function handleDrop(event: DragEvent<HTMLLabelElement>) {
    event.preventDefault();
    onDragStateChange(false);
    onFiles(Array.from(event.dataTransfer.files));
  }

  return (
    <label
      className={`apoema-dropzone ${dragging ? "is-dragging" : ""}`}
      onDragOver={(event) => {
        event.preventDefault();
        onDragStateChange(true);
      }}
      onDragLeave={() => onDragStateChange(false)}
      onDrop={handleDrop}
    >
      <UploadCloud size={18} />
      <span>{label}</span>
      <small>PDF, DOCX, XLSX, PNG, CSV e anexos controlados</small>
      <input type="file" multiple onChange={handleChange} hidden />
      <Paperclip size={16} />
    </label>
  );
}
