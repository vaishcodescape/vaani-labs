export function scriptColorClasses(script: string): string {
  switch (script) {
    case "Devanagari":
      return "bg-orange-50 text-orange-800 border-orange-200";
    case "Gujarati":
      return "bg-violet-50 text-violet-800 border-violet-200";
    case "Latin":
      return "bg-sky-50 text-sky-800 border-sky-200";
    default:
      return "bg-slate-50 text-slate-600 border-slate-200";
  }
}
