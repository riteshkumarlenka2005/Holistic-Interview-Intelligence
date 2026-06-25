/// <reference types="astro/client" />

interface PageMetadata {
  pageIdentifier?: string;
  title?: string;
  description?: string;
}

declare global {
  interface ImportMeta {
    readonly env: ImportMetaEnv;
  }

  interface ImportMetaEnv {
    readonly BASE_NAME: string;
    readonly OPENROUTER_API_KEY: string;
    readonly FRONTEND_URL: string;
  }
}

export {};

declare module "react-router-dom" {
  export interface IndexRouteObject {
    routeMetadata?: PageMetadata;
  }
  export interface NonIndexRouteObject {
    routeMetadata?: PageMetadata;
  }
}
