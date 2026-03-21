import { z } from "zod";

export const uploadSchema = z.object({
  file: z
    .custom<File>((v) => v instanceof File, {
      message: "Se requiere un archivo",
    })
    .refine((file) => file.size < 50 * 1024 * 1024, {
      message: "El archivo no debe pesar más de 50MB",
    })
    .refine(
      (file) =>
        ["application/pdf", "image/vnd.dwg", "image/vnd.dxf"].includes(file.type) ||
        file.name.endsWith(".dxf") ||
        file.name.endsWith(".dwg"),
      {
        message: "El archivo debe ser PDF, DWG o DXF",
      }
    ),
});

export type UploadData = z.infer<typeof uploadSchema>;
