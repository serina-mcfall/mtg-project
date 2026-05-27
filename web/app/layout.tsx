import type { Metadata } from 'next'
import { Cinzel, Andika, EB_Garamond } from 'next/font/google'
import './globals.css'

const cinzel = Cinzel({
  variable: '--font-cinzel',
  weight: ['400', '500', '600', '700'],
  subsets: ['latin'],
  display: 'swap',
})

const andika = Andika({
  variable: '--font-andika',
  weight: ['400', '700'],
  style: ['normal', 'italic'],
  subsets: ['latin'],
  display: 'swap',
})

const ebGaramond = EB_Garamond({
  variable: '--font-eb-garamond',
  weight: ['400', '500'],
  style: ['normal', 'italic'],
  subsets: ['latin'],
  display: 'swap',
})

export const metadata: Metadata = {
  title: 'MTG Project',
  description: 'A calm personal Magic: The Gathering database — Phase 1A',
}

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode
}>) {
  return (
    <html
      lang="en"
      data-theme="dark"
      className={`${cinzel.variable} ${andika.variable} ${ebGaramond.variable}`}
    >
      <body>{children}</body>
    </html>
  )
}
