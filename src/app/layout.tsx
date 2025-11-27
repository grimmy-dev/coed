import type { Metadata } from "next";
import { Delius, Geist_Mono } from "next/font/google";
import "./globals.css";

const font = Delius({
  subsets: ["latin"],
  weight: ["400"],
});

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
});

export const metadata: Metadata = {
  title: "Collaborative Code Editor",
  description: "Real-time collaborative code editing with WebSocket",
};


export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body
        className={`${font.className} ${geistMono.variable} dark antialiased`}
      >
        {children}
      </body>
    </html>
  );
}
