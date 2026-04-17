'use client';

import { SignedIn, SignedOut, SignInButton } from '@clerk/nextjs';
import ChatLayout from '@/components/ChatLayout';
import {
  Scale,
  Calculator,
  FileText,
  Shield,
  ArrowRight,
  IndianRupee,
  BookOpen,
  FileCheck,
  Users,
} from 'lucide-react';

function LandingPage() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-slate-100">
      {/* Header */}
      <header className="flex items-center justify-between px-6 py-4 max-w-6xl mx-auto">
        <div className="flex items-center gap-2">
          <Scale className="text-primary-600" size={28} />
          <span className="text-xl font-bold text-slate-800">FinLex AI</span>
        </div>
        <SignInButton mode="modal">
          <button className="px-5 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition font-medium text-sm">
            Sign In
          </button>
        </SignInButton>
      </header>

      {/* Hero */}
      <main className="max-w-6xl mx-auto px-6 pt-16 pb-20">
        <div className="text-center mb-16">
          <div className="inline-flex items-center gap-2 bg-primary-100 text-primary-700 px-4 py-1.5 rounded-full text-sm font-medium mb-6">
            <IndianRupee size={14} />
            Built for Indian Professionals
          </div>
          <h1 className="text-4xl md:text-5xl font-bold text-slate-900 mb-4 leading-tight">
            AI Assistant for<br />
            <span className="text-primary-600">Accounting</span> &{' '}
            <span className="text-amber-600">Law</span>
          </h1>
          <p className="text-lg text-slate-600 max-w-2xl mx-auto mb-8">
            Calculate income tax, draft legal notices, compute GST, compare tax regimes,
            and get instant answers on Indian tax and legal compliance — all powered by AI.
          </p>
          <SignInButton mode="modal">
            <button className="inline-flex items-center gap-2 px-8 py-3 bg-primary-600 text-white rounded-xl hover:bg-primary-700 transition font-semibold text-base shadow-lg shadow-primary-200">
              Get Started Free
              <ArrowRight size={18} />
            </button>
          </SignInButton>
        </div>

        {/* Features Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mb-16">
          {[
            {
              icon: Calculator,
              title: 'Income Tax Calculator',
              desc: 'FY 2025-26 slabs with surcharge, cess, and rebate. Compare old vs new regime instantly.',
              color: 'bg-emerald-100 text-emerald-600',
            },
            {
              icon: IndianRupee,
              title: 'GST & TDS Tools',
              desc: 'Post-GST 2.0 rates, reverse charge mechanism, TDS on 19+ payment types with PAN checks.',
              color: 'bg-blue-100 text-blue-600',
            },
            {
              icon: FileText,
              title: 'Legal Document Drafting',
              desc: 'Draft legal notices, NDAs, board resolutions, and engagement letters with proper Indian law references.',
              color: 'bg-amber-100 text-amber-600',
            },
            {
              icon: BookOpen,
              title: 'Knowledge Base',
              desc: 'Upload your documents (PDF, DOCX, Excel) and ask questions against them with AI-powered RAG.',
              color: 'bg-purple-100 text-purple-600',
            },
            {
              icon: FileCheck,
              title: 'Compliance Calendar',
              desc: 'ITR, GSTR-1, GSTR-3B, TDS return due dates, tax audit deadlines — all at your fingertips.',
              color: 'bg-rose-100 text-rose-600',
            },
            {
              icon: Shield,
              title: 'Secure & Private',
              desc: 'Your data stays yours. Tenant-isolated architecture with enterprise-grade authentication.',
              color: 'bg-slate-100 text-slate-600',
            },
          ].map((feature, idx) => (
            <div
              key={idx}
              className="bg-white rounded-xl p-6 border border-slate-200 hover:shadow-md transition"
            >
              <div className={`w-10 h-10 rounded-lg ${feature.color} flex items-center justify-center mb-4`}>
                <feature.icon size={20} />
              </div>
              <h3 className="font-semibold text-slate-800 mb-2">{feature.title}</h3>
              <p className="text-sm text-slate-500 leading-relaxed">{feature.desc}</p>
            </div>
          ))}
        </div>

        {/* CTA */}
        <div className="text-center bg-white rounded-2xl p-10 border border-slate-200 shadow-sm">
          <h2 className="text-2xl font-bold text-slate-800 mb-3">
            Ready to streamline your practice?
          </h2>
          <p className="text-slate-500 mb-6">
            Join CAs, lawyers, and tax professionals who use FinLex AI daily.
          </p>
          <SignInButton mode="modal">
            <button className="inline-flex items-center gap-2 px-8 py-3 bg-primary-600 text-white rounded-xl hover:bg-primary-700 transition font-semibold shadow-lg shadow-primary-200">
              Start Using FinLex AI
              <ArrowRight size={18} />
            </button>
          </SignInButton>
        </div>
      </main>

      {/* Footer */}
      <footer className="border-t border-slate-200 py-6 text-center text-sm text-slate-400">
        © 2026 FinLex AI · Built for Indian Accounting & Law Professionals
      </footer>
    </div>
  );
}

export default function Home() {
  return (
    <>
      <SignedOut>
        <LandingPage />
      </SignedOut>
      <SignedIn>
        <ChatLayout />
      </SignedIn>
    </>
  );
}
