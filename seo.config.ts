export interface PageMetaConfig {
  title?: string;
  description?: string;
  type?: string;
  url?: string;
  image?: string;
  imageType?: string;
  imageWidth?: number;
  imageHeight?: number;
  imageAlt?: string;
  twitterCard?: "summary" | "summary_large_image" | "app" | "player";
}

export interface ResolvedPageMeta {
  siteName: string;
  title: string;
  description: string;
  type: string;
  url: string;
  image: string;
  imageSecureUrl: string;
  imageType: string;
  imageWidth: number;
  imageHeight: number;
  imageAlt: string;
  twitterCard: "summary" | "summary_large_image" | "app" | "player";
}

export const SITE_ORIGIN = "https://ipl-winner-prediction-ten.vercel.app";

export const DEFAULT_META: ResolvedPageMeta = {
  siteName: "IPL-Winner-Prediction",
  title: "IPL 2026 Winner Prediction — Temporal ML System",
  description:
    'This is a technical implementation of a dynamic machine learning system designed to model team strength and simulate IPL 2026 outcomes. The project focuses on Strict Temporal Feature Engineering to eliminate data leakage and captures the high-scoring, volatile trends of the modern "Impact Player" era.',
  type: "website",
  url: `${SITE_ORIGIN}/`,
  image: `${SITE_ORIGIN}/assets/Dashboard.png`,
  imageSecureUrl: `${SITE_ORIGIN}/assets/Dashboard.png`,
  imageType: "image/png",
  imageWidth: 1919,
  imageHeight: 918,
  imageAlt:
    "IPL 2026 Winner Prediction dashboard showing win probabilities, model metrics, and match forecasts",
  twitterCard: "summary_large_image",
};

/**
 * Per-route metadata overrides. Any omitted field falls back to DEFAULT_META.
 */
export const PAGE_META: Record<string, PageMetaConfig> = {
  "/": {},
  "/teams": {
    title: "Teams — IPL 2026 Winner Prediction",
    description:
      "Predicted IPL 2026 standings, title probabilities, and form confidence across all 10 franchises.",
  },
  "/players": {
    title: "Players — IPL 2026 Winner Prediction",
    description:
      "Impact-ranked IPL player index with rolling form scores, role filters, and performance metrics.",
  },
  "/simulator": {
    title: "Match Simulator — IPL 2026 Winner Prediction",
    description:
      "Simulate head-to-head IPL 2026 matchups across venues using temporal strength ratings.",
  },
  "/archive": {
    title: "Historical Archive — IPL 2026 Winner Prediction",
    description:
      "Historical IPL seasons from 2008 to 2026 with champions, runners-up, and model validation accuracy.",
  },
  "/about": {
    title: "About the Model — IPL 2026 Winner Prediction",
    description:
      "Technical overview of the calibrated temporal ensemble, 42 engineered features, and back-tested IPL match accuracy.",
  },
  "/intelligence": {
    title: "Team Intelligence — IPL 2026 Winner Prediction",
    description:
      "Squad strength, playoff qualification rates, and qualitative form signals across IPL franchises.",
  },
  "/analytics": {
    title: "Analytics — IPL 2026 Winner Prediction",
    description:
      "Historical win rates, feature importance, and model diagnostics across IPL seasons.",
  },
  "/insights": {
    title: "Visual Insights — IPL 2026 Winner Prediction",
    description:
      "SHAP explainability summaries, model comparisons, and win probability visualizations.",
  },
  "/leaderboard": {
    title: "Model Leaderboard — IPL 2026 Winner Prediction",
    description:
      "Cross-validated accuracy, ROC-AUC, and F1 benchmarks across ensemble and tree-based models.",
  },
};

function toAbsoluteHttpsUrl(pathOrUrl: string): string {
  if (/^https:\/\//i.test(pathOrUrl)) {
    return pathOrUrl;
  }
  if (/^http:\/\//i.test(pathOrUrl)) {
    return pathOrUrl.replace(/^http:\/\//i, "https://");
  }
  const normalizedPath = pathOrUrl.startsWith("/") ? pathOrUrl : `/${pathOrUrl}`;
  return `${SITE_ORIGIN}${normalizedPath}`;
}

export function resolvePageMeta(routePath: string): ResolvedPageMeta {
  const normalizedRoute = routePath === "/" ? "/" : `/${routePath.replace(/^\/+|\/+$/g, "")}`;
  const override = PAGE_META[normalizedRoute] ?? {};

  const url = override.url ? toAbsoluteHttpsUrl(override.url) : toAbsoluteHttpsUrl(normalizedRoute);
  const image = override.image ? toAbsoluteHttpsUrl(override.image) : DEFAULT_META.image;

  return {
    siteName: DEFAULT_META.siteName,
    title: override.title ?? DEFAULT_META.title,
    description: override.description ?? DEFAULT_META.description,
    type: override.type ?? DEFAULT_META.type,
    url,
    image,
    imageSecureUrl: image,
    imageType: override.imageType ?? DEFAULT_META.imageType,
    imageWidth: override.imageWidth ?? DEFAULT_META.imageWidth,
    imageHeight: override.imageHeight ?? DEFAULT_META.imageHeight,
    imageAlt: override.imageAlt ?? DEFAULT_META.imageAlt,
    twitterCard: override.twitterCard ?? DEFAULT_META.twitterCard,
  };
}

function escapeHtml(value: string): string {
  return value
    .replace(/&/g, "&amp;")
    .replace(/"/g, "&quot;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;");
}

export function renderMetaTags(meta: ResolvedPageMeta): string {
  const title = escapeHtml(meta.title);
  const description = escapeHtml(meta.description);
  const siteName = escapeHtml(meta.siteName);
  const type = escapeHtml(meta.type);
  const url = escapeHtml(meta.url);
  const image = escapeHtml(meta.image);
  const imageSecureUrl = escapeHtml(meta.imageSecureUrl);
  const imageType = escapeHtml(meta.imageType);
  const imageAlt = escapeHtml(meta.imageAlt);
  const twitterCard = escapeHtml(meta.twitterCard);

  return [
    `    <title>${title}</title>`,
    `    <meta name="description" content="${description}" />`,
    `    <link rel="canonical" href="${url}" />`,
    `    <meta property="og:type" content="${type}" />`,
    `    <meta property="og:site_name" content="${siteName}" />`,
    `    <meta property="og:title" content="${title}" />`,
    `    <meta property="og:description" content="${description}" />`,
    `    <meta property="og:url" content="${url}" />`,
    `    <meta property="og:image" content="${image}" />`,
    `    <meta property="og:image:secure_url" content="${imageSecureUrl}" />`,
    `    <meta property="og:image:type" content="${imageType}" />`,
    `    <meta property="og:image:width" content="${meta.imageWidth}" />`,
    `    <meta property="og:image:height" content="${meta.imageHeight}" />`,
    `    <meta property="og:image:alt" content="${imageAlt}" />`,
    `    <meta name="twitter:card" content="${twitterCard}" />`,
    `    <meta name="twitter:title" content="${title}" />`,
    `    <meta name="twitter:description" content="${description}" />`,
    `    <meta name="twitter:image" content="${image}" />`,
    `    <meta name="twitter:image:alt" content="${imageAlt}" />`,
  ].join("\n");
}
