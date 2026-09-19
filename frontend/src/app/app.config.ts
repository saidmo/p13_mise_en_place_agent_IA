import { ApplicationConfig, provideBrowserGlobalErrorListeners } from '@angular/core';
import { provideHttpClient } from '@angular/common/http';   // HttpClient

export const appConfig: ApplicationConfig = {
  providers: [
    provideHttpClient(),                                    
    provideBrowserGlobalErrorListeners(),
  ]
};
