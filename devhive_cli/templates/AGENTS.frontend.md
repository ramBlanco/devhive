# Frontend Architecture & AI Agent Guidelines

This `AGENTS.md` (or `GUIDELINES.md`) file serves as the strict instruction manual for OpenCode and DevHive agents. It defines the technical stack, architectural patterns, and coding conventions for this frontend project.

## 🛠️ 1. Tech Stack
- **Framework**: Next.js 15 (App Router)
- **Library**: React 19
- **Language**: TypeScript (Strict Mode)
- **Styling**: Tailwind CSS v3/v4 + `clsx` + `tailwind-merge`
- **Components**: shadcn/ui (Radix UI primitives)
- **Icons**: Lucide React
- **Data Fetching**: React Server Components (RSC) & Server Actions

## 🧠 2. OpenCode Skills to Load
Agents **MUST** load the following specialized skills before executing tasks:
- `frontend-developer`: For modern React 19 / Next.js 15 patterns.
- `frontend-design`: For high-quality, non-generic UI aesthetics.
- `shadcn`: For proper installation and composition of shadcn/ui components.
- `theme-factory`: For applying cohesive color palettes and typography.
- `architecture-patterns`: For maintaining clean separation of concerns.

## 📂 3. Project Structure (Feature-Based Architecture)
For maximum scalability and maintainability, the project follows a feature-based architecture within the `src/` directory. 

```text
src/
├── app/                  # Next.js App Router (Pages, Layouts, API Routes)
│   ├── (auth)/           # Route groups for logical separation
│   ├── dashboard/        # Dashboard routes
│   └── layout.tsx        # Root layout (Providers, Fonts, Metadata)
├── components/           
│   ├── ui/               # Pure shadcn/ui components (DO NOT EDIT DIRECTLY unless styling)
│   └── shared/           # Reusable global components (Navbar, Footer, etc.)
├── features/             # Feature-based modules (THE CORE OF THE APP)
│   ├── users/            # "Users" feature module
│   │   ├── actions.ts    # Server Actions for this feature
│   │   ├── components/   # Feature-specific React components
│   │   └── types.ts      # Feature-specific TypeScript interfaces
│   └── products/         # "Products" feature module
├── lib/                  # Utility functions (utils.ts, formatting, constants)
└── hooks/                # Global custom React hooks
```

## 📐 4. Architectural Rules & Best Practices

1. **Default to Server Components (RSC)**: 
   - All components inside `app/` and `features/` MUST be Server Components by default to optimize bundle size and SEO.
   - ONLY add the `"use client"` directive at the very top of a file if the component requires interactivity (`useState`, `useEffect`, `onClick`, browser APIs).
   - Keep Client Components as low in the tree (leaf nodes) as possible.

2. **Server Actions for Mutations**:
   - Do NOT build traditional API routes (`route.ts`) for internal app data mutations.
   - Use Next.js Server Actions (`"use server"`) placed in `src/features/[name]/actions.ts`.
   - Always validate inputs inside Server Actions (using Zod or similar) before mutating data.

3. **Shadcn/ui Usage**:
   - Use the OpenCode CLI or `npx shadcn@latest add [component]` to install components.
   - Combine UI components to build complex blocks (e.g., combining `Card`, `Button`, and `Input` to make a LoginForm).

4. **Type Safety**:
   - Avoid `any`. Define interfaces/types in `types.ts` files.
   - Export types and reuse them across Server Actions and Client Components.

## 💻 5. Code Examples

### Example A: Data Fetching in a Server Component (RSC)
*File: `src/app/dashboard/page.tsx`*
```tsx
import { Suspense } from "react";
import { getUserProfile } from "@/features/users/actions";
import { UserProfileCard } from "@/features/users/components/user-profile-card";
import { Skeleton } from "@/components/ui/skeleton";

// This is a Server Component (no "use client")
export default async function DashboardPage() {
  // Fetch data directly on the server
  const user = await getUserProfile();

  return (
    <main className="container mx-auto p-6">
      <h1 className="text-3xl font-bold mb-6">Dashboard</h1>
      <Suspense fallback={<Skeleton className="h-[200px] w-full rounded-xl" />}>
        <UserProfileCard user={user} />
      </Suspense>
    </main>
  );
}
```

### Example B: Server Action for Data Mutation
*File: `src/features/users/actions.ts`*
```typescript
"use server";

import { revalidatePath } from "next/cache";

export type UpdateUserResponse = {
  success: boolean;
  message: string;
};

export async function updateUserName(formData: FormData): Promise<UpdateUserResponse> {
  const newName = formData.get("name") as string;
  
  if (!newName || newName.length < 3) {
    return { success: false, message: "Name must be at least 3 characters." };
  }

  // Perform database mutation here...
  // await db.user.update(...)

  // Revalidate the cache so the UI updates instantly
  revalidatePath("/dashboard");

  return { success: true, message: "Profile updated successfully." };
}
```

### Example C: Client Component using Shadcn/ui & Server Actions
*File: `src/features/users/components/edit-name-form.tsx`*
```tsx
"use client";

import { useState, useTransition } from "react";
import { updateUserName } from "@/features/users/actions";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { toast } from "@/components/ui/use-toast"; // shadcn toast

export function EditNameForm() {
  const [isPending, startTransition] = useTransition();

  const handleSubmit = (formData: FormData) => {
    startTransition(async () => {
      const result = await updateUserName(formData);
      
      if (result.success) {
        toast({ title: "Success", description: result.message });
      } else {
        toast({ title: "Error", description: result.message, variant: "destructive" });
      }
    });
  };

  return (
    <form action={handleSubmit} className="flex gap-4 items-center">
      <Input 
        name="name" 
        placeholder="Enter new name" 
        required 
        disabled={isPending} 
        className="max-w-sm"
      />
      <Button type="submit" disabled={isPending}>
        {isPending ? "Saving..." : "Save Name"}
      </Button>
    </form>
  );
}
```
