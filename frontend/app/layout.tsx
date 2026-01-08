import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Cogniveil WorkflowBuilder",
  description: "Build and visualize AI workflows by Cogniveil",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" suppressHydrationWarning>
      <body>{children}</body>
    </html>
  );
}
