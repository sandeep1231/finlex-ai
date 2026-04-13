'use client';

import { SignedIn, SignedOut, RedirectToSignIn } from '@clerk/nextjs';
import ChatLayout from '@/components/ChatLayout';

export default function Home() {
  return (
    <>
      <SignedOut>
        <RedirectToSignIn />
      </SignedOut>
      <SignedIn>
        <ChatLayout />
      </SignedIn>
    </>
  );
}
