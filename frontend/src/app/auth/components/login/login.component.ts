import { Component } from '@angular/core';
import { Router } from '@angular/router';
import { MatInputModule } from '@angular/material/input';
import { MatIconModule } from '@angular/material/icon';
import { MatButtonModule } from '@angular/material/button';
import { takeUntilDestroyed } from '@angular/core/rxjs-interop';
import { FormControl, Validators, ReactiveFormsModule } from '@angular/forms';
import { AuthService } from '../../services/auth.service';


@Component({
  selector: 'app-login',
  standalone: true,
  imports: [
    MatInputModule,
    MatIconModule,
    ReactiveFormsModule,
    MatButtonModule
  ],
  templateUrl: './login.component.html',
  styleUrl: './login.component.css',
})


export class LoginComponent {

  // Form variables and error messages
  email = new FormControl('', [Validators.required, Validators.email]);
  errorMessageEmail = '';

  password = new FormControl('', [Validators.required]);
  errorMessagePassword = '';

  // State varible to hide or show password
  hide = true;


  // -------------------------------------------------------------------- //
  //          CONSTRUCTOR: Validate the state of form variables           //
  // -------------------------------------------------------------------- //
  constructor(private router: Router, private authService: AuthService) {
    this.email.valueChanges
      .pipe(takeUntilDestroyed())
      .subscribe(() => this.updateErrorMessageEmail());

    this.password.valueChanges
      .pipe(takeUntilDestroyed())
      .subscribe(() => this.updateErrorMessagePassword());
  }


  // -------------------------------------------------------------------- //
  //           METHODS: Update status and erros in form values            //
  // -------------------------------------------------------------------- //
  updateErrorMessageEmail() {
    this.errorMessageEmail = this.email.hasError('required')
      ? 'Debe ingresar un correo'
      : this.email.hasError('email')
        ? 'Correo no válido'
        : '';
  }
  updateErrorMessagePassword() {
    this.errorMessagePassword = this.password.hasError('required')
      ? 'Debe ingresar una contraseña'
      : '';
  }


  // -------------------------------------------------------------------- //
  //           METHOD: Show the register form (Create new user)           //
  // -------------------------------------------------------------------- //
  redirectToRegister() {
    this.router.navigateByUrl('/register');
  }


  // -------------------------------------------------------------------- //
  //            METHOD: User authentication and JWT generation            //
  // -------------------------------------------------------------------- //
  login() {
    const email = this.email.value;
    const password = this.password.value;

    if (email && password) {
      this.authService.get_token(email, password).subscribe({
        next: (token) => {
          this.authService.login(token.token);
        },
        error: (err) => {
          console.error("Error during login:", err);
        },
        complete: () =>{
          console.log("Login successfully");
          this.router.navigateByUrl('/apps');
        }
      });
    }
  }


}