import type { Metadata, Viewport } from "next";
import { ReactNode } from "react";
import "@/styles/globals.css";
import { AppShell } from "@/components/AppShell";

export const metadata: Metadata = {
  title: "StudyBrain Web",
  description: "Aplicación mobile-first para estudiar con agentes IA",
  applicationName: "StudyBrain Web",
  appleWebApp: {
    capable: true,
    title: "StudyBrain Web",
    statusBarStyle: "black-translucent"
  }
};

export const viewport: Viewport = {
  themeColor: "#020617",
  width: "device-width",
  initialScale: 1,
  maximumScale: 1
};

export default function RootLayout({ children }: { children: ReactNode }): ReactNode {
  return (
    <html lang="es">
      <body>
        <AppShell>{children}</AppShell>
      </body>
    </html>
  );
}
