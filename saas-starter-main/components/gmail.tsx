"use client";

import { signIn, signOut, useSession } from "next-auth/react";
import { useState, useEffect } from "react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Loader2, LogIn, LogOut, Mail, RotateCw } from "lucide-react";
import { motion } from "framer-motion";

export default function Gmail() {
  const { data: session } = useSession();
  const [emails, setEmails] = useState<{ id: string; snippet: string }[]>([]);
  const [loading, setLoading] = useState(false);

  const fetchEmails = async () => {
    setLoading(true);
    const res = await fetch("/api/gmail");
    if (res.ok) {
      const data = await res.json();
      setEmails(data);
    }
    setLoading(false);
  };

  // Load emails automatically on page load
  useEffect(() => {
    if (session) fetchEmails();
  }, [session]);

  return (
    <div className="flex flex-col items-center justify-center min-h-screen p-4 bg-gray-100 dark:bg-gray-900">
      <Card className="w-full max-w-lg shadow-lg border border-gray-200 dark:border-gray-700">
        <CardHeader className="flex justify-between items-center">
          <CardTitle className="text-xl font-semibold text-gray-900 dark:text-gray-100">
            Gmail Inbox
          </CardTitle>
          {session && (
            <Button
              variant="ghost"
              size="icon"
              onClick={fetchEmails}
              disabled={loading}
              className="hover:bg-gray-200 dark:hover:bg-gray-800"
            >
              <RotateCw className={`h-5 w-5 ${loading ? "animate-spin" : ""}`} />
            </Button>
          )}
        </CardHeader>
        <CardContent className="flex flex-col items-center space-y-4">
          {session ? (
            <>
              <p className="text-gray-700 dark:text-gray-300">
                Welcome, <span className="font-semibold">{session.user?.name}</span>
              </p>
              <Button onClick={() => signOut()} variant="destructive" className="w-full">
                <LogOut className="mr-2 h-5 w-5" />
                Sign Out
              </Button>
              <div className="w-full">
                {emails.length > 0 ? (
                  <motion.ul
                    className="mt-4 space-y-3"
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    transition={{ duration: 0.5 }}
                  >
                    {emails.map((email) => (
                      <motion.li
                        key={email.id}
                        className="p-3 bg-gray-50 dark:bg-gray-800 rounded-md border border-gray-200 dark:border-gray-700 shadow-sm"
                        whileHover={{ scale: 1.02 }}
                        whileTap={{ scale: 0.98 }}
                      >
                        {email.snippet}
                      </motion.li>
                    ))}
                  </motion.ul>
                ) : (
                  <p className="text-gray-500 dark:text-gray-400 text-center">
                    No emails found.
                  </p>
                )}
              </div>
            </>
          ) : (
            <Button onClick={() => signIn("google")} className="w-full">
              <LogIn className="mr-2 h-5 w-5" />
              Sign in with Google
            </Button>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
