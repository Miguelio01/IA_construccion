"use server";

import { uploadSchema } from "@/lib/schemas";
import { z } from "zod";

type UploadResult = {
  success: boolean;
  message: string;
  errors?: Record<string, string[]>;
};

export async function uploadStructuralFile(
  prevState: UploadResult | null,
  formData: FormData
): Promise<UploadResult> {
  try {
    const file = formData.get("file") as File | null;
    if (!file) {
      return { success: false, message: "No se proporcionó ningún archivo." };
    }

    // 1. Validar el archivo usando Zod de manera estricta
    const validatedFields = uploadSchema.safeParse({ file });

    if (!validatedFields.success) {
      return {
        success: false,
        message: "Error de validación.",
        errors: validatedFields.error.flatten().fieldErrors,
      };
    }

    // 2. Aquí llamaríamos al BFF (Orchestrator) para enviar el archivo al pipeline de ML.
    // Ej: await fetch('http://localhost:4000/api/upload', { ... })
    // Simulamos un retraso
    await new Promise((resolve) => setTimeout(resolve, 1000));

    console.log(`Archivo validado: ${file.name} (${file.size} bytes)`);

    return {
      success: true,
      message: `El archivo ${file.name} se ha subido correctamente y está siendo procesado por el modelo de inferencia.`,
    };

  } catch (error: unknown) {
    // 3. Manejo estricto de excepciones
    console.error("Error crítico durante la subida del archivo:", error);
    let errorMessage = "Ocurrió un error inesperado al procesar el archivo.";
    if (error instanceof Error) {
      errorMessage = error.message;
    }
    return {
      success: false,
      message: errorMessage,
    };
  }
}
