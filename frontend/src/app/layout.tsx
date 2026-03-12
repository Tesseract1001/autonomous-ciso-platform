import type { Metadata } from "next";
import { Inter, Space_Grotesk } from "next/font/google";
import "./globals.css";

const inter = Inter({ subsets: ["latin"], variable: "--font-inter" });
const spaceGrotesk = Space_Grotesk({ subsets: ["latin"], variable: "--font-space" });

export const metadata: Metadata = {
  title: "Virtual CISO | Autonomous Intelligence",
  description: "Autonomous Secure Software Intelligence and Assurance Platform",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body
        className={`${inter.variable} ${spaceGrotesk.variable} antialiased min-h-screen text-slate-300`}
      >
        <div className="flex h-screen overflow-hidden">
          {/* Main Layout Wrapper */}
          <main className="flex-1 overflow-y-auto w-full relative">
            {children}
          </main>
        </div>
      </body>
    </html>
  );
}
