import { CanActivateFn, Router } from '@angular/router';
import { AuthService } from '../services/auth.service';
import { inject } from '@angular/core';

export const authGuard: CanActivateFn = (route, state) => {
  // Service injection
  const authService = inject(AuthService)
  const router = inject(Router)

  // Determine if user is authenticated
  if (authService.isAuth()) {
    return true
  } else{
    return router.createUrlTree(["/"])
  }
};
