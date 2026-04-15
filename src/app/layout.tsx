import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Calidefy",
  description: "The Intuitive, AI-Powered Calendar",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body className="antialiased">
        {children}
      </body>
    </html>
  );
}