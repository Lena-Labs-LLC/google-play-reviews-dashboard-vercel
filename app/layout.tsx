import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Google Play Reviews Dashboard",
  description: "Manage your Google Play app reviews with AI",
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
