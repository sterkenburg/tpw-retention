import { NextResponse } from "next/server";
import type { NextRequest } from "next/server";

// HTTP Basic Auth gate for the whole dashboard.
//
// Next.js 16 renamed `middleware` to `proxy`; this runs on the Node.js runtime.
//
// Credentials come from environment variables so the password is never
// committed. Set these in Vercel (Project → Settings → Environment Variables):
//   BASIC_AUTH_USER
//   BASIC_AUTH_PASSWORD
//
// Fails closed: if BASIC_AUTH_PASSWORD is unset, every request is rejected
// rather than served unprotected.

function unauthorized(): NextResponse {
  return new NextResponse("Authentication required.", {
    status: 401,
    headers: {
      "WWW-Authenticate": 'Basic realm="TPW Supplier Health", charset="UTF-8"',
    },
  });
}

// Length-safe constant-time-ish string compare to avoid leaking length/timing.
function safeEqual(a: string, b: string): boolean {
  if (a.length !== b.length) return false;
  let mismatch = 0;
  for (let i = 0; i < a.length; i++) {
    mismatch |= a.charCodeAt(i) ^ b.charCodeAt(i);
  }
  return mismatch === 0;
}

export function proxy(req: NextRequest): NextResponse {
  const expectedUser = process.env.BASIC_AUTH_USER ?? "";
  const expectedPassword = process.env.BASIC_AUTH_PASSWORD ?? "";

  // No password configured → refuse to serve anything (fail closed).
  if (!expectedPassword) {
    return unauthorized();
  }

  const header = req.headers.get("authorization");
  if (header?.startsWith("Basic ")) {
    try {
      const decoded = Buffer.from(
        header.slice("Basic ".length),
        "base64",
      ).toString("utf-8");
      const separator = decoded.indexOf(":");
      const user = separator === -1 ? decoded : decoded.slice(0, separator);
      const password = separator === -1 ? "" : decoded.slice(separator + 1);

      const userOk = safeEqual(user, expectedUser);
      const passwordOk = safeEqual(password, expectedPassword);
      if (userOk && passwordOk) {
        return NextResponse.next();
      }
    } catch {
      // Malformed header → fall through to 401.
    }
  }

  return unauthorized();
}

export const config = {
  // Protect everything except Next.js internals and the favicon.
  matcher: ["/((?!_next/static|_next/image|favicon.ico).*)"],
};
