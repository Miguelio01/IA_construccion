"use client";

import { useActionState, useEffect } from "react";
import { uploadStructuralFile } from "@/app/actions/upload";

export default function UploadForm() {
  const [state, formAction, isPending] = useActionState(uploadStructuralFile, null);

  useEffect(() => {
    if (state?.success) {
      alert(state.message);
    } else if (state?.errors) {
      alert(state.message + "\n" + JSON.stringify(state.errors));
    } else if (state && !state.success) {
      alert(state.message);
    }
  }, [state]);

  return (
    <form action={formAction} className="flex flex-col gap-4 max-w-md mx-auto p-4 border rounded-xl shadow-sm bg-white text-gray-800">
      <h2 className="text-xl font-bold">Subir Planos Estructurales</h2>
      <p className="text-sm text-gray-500">Sube tus archivos DWG, DXF o PDF para que sean analizados por el modelo de ML.</p>

      <div className="flex flex-col gap-2">
        <label htmlFor="file" className="font-medium text-sm">Selecciona un archivo</label>
        <input
          type="file"
          id="file"
          name="file"
          accept=".pdf,.dwg,.dxf"
          className="file:mr-4 file:py-2 file:px-4 file:rounded-full file:border-0 file:text-sm file:font-semibold file:bg-blue-50 file:text-blue-700 hover:file:bg-blue-100"
          required
        />
        {state?.errors?.file && (
          <p className="text-red-500 text-xs mt-1">{state.errors.file[0]}</p>
        )}
      </div>

      <button
        type="submit"
        disabled={isPending}
        className="mt-4 bg-blue-600 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded transition-colors disabled:bg-blue-300 disabled:cursor-not-allowed"
      >
        {isPending ? "Analizando y Subiendo..." : "Procesar Plano"}
      </button>

      {state && !state.success && !state.errors && (
        <p className="text-red-600 text-sm mt-2">{state.message}</p>
      )}
    </form>
  );
}
