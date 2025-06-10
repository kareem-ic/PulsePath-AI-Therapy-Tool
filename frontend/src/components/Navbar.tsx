'use client'
import Link from 'next/link'
import { usePathname } from 'next/navigation'

const links = [
  { href: '/', label: 'Home' },
  { href: '/journal', label: 'Mood Journal' },
  { href: '/chat', label: 'Therapy Chat' },
]

export default function Navbar() {
  const pathname = usePathname()

  return (
    <header className="sticky top-0 z-30 bg-white/80 backdrop-blur">
      <nav className="mx-auto flex max-w-6xl items-center justify-between px-4 py-3">
        <Link
          href="/"
          className="inline-flex items-center text-xl font-semibold"
        >
          {/* new logo svg lives in /public */}
          <img src="/logo.svg" alt="" className="mr-2 h-7 w-7" />
          <span className="text-brand-700">PulsePath</span>
        </Link>

        <ul className="flex gap-6 text-sm font-medium">
          {links.map(({ href, label }) => (
            <li key={href}>
              <Link
                href={href}
                className={`${
                  pathname === href
                    ? 'text-brand-700'
                    : 'text-gray-700 hover:text-brand-600'
                } transition-colors`}
              >
                {label}
              </Link>
            </li>
          ))}
        </ul>
      </nav>
    </header>
  )
}
