import { Component } from '@angular/core';
import { ActivatedRoute } from '@angular/router';
import { HeaderComponent } from '../../shared/header/header.component';

import { Router } from '@angular/router';
import { MatInputModule } from '@angular/material/input';
import { MatIconModule } from '@angular/material/icon';
import { MatButtonModule } from '@angular/material/button';
import { takeUntilDestroyed } from '@angular/core/rxjs-interop';
import { FormControl, Validators, ReactiveFormsModule } from '@angular/forms';
import { AuthService } from '../../auth/auth.service';


@Component({
  selector: 'app-login-redirect',
  standalone: true,
  imports: [
    HeaderComponent,
    MatInputModule,
    MatIconModule,
    ReactiveFormsModule,
    MatButtonModule
  ],
  templateUrl: './login-redirect.component.html',
  styleUrl: './login-redirect.component.css'
})
export class LoginRedirectComponent {

  // -------------------------------------------------------------------- //
  //                           CLASS ATTRIBUTES                           //
  // -------------------------------------------------------------------- //
  // State variables
  loginPanelActive:boolean = false;
  isAuth:boolean = false;
  nextLink: string | null | undefined;

  // Form variables and error messages
  email = new FormControl('', [Validators.required, Validators.email]);
  password = new FormControl('', [Validators.required]);
  errorMessageEmail = '';

  // State varible to hide or show password
  hide = true;

  // Authentication error variable
  authErr = false;



  // -------------------------------------------------------------------- //
  //                            CONSTRUCTOR                               //
  // -------------------------------------------------------------------- //
  constructor(private route: ActivatedRoute, private router: Router, private authService: AuthService) {
    this.email.valueChanges
      .pipe(takeUntilDestroyed())
      .subscribe(() => this.updateErrorMessageEmail());
  }
  ngOnInit(): void {
    this.route.queryParamMap.subscribe(params => {
      this.nextLink = params.get('next');
    });
  }



  // -------------------------------------------------------------------- //
  //                               METHODS                                //
  // -------------------------------------------------------------------- //
  retrieveIsAuth(isAuthD:boolean){
    this.isAuth = isAuthD;
  }

  showLoginPanel(click:string){
    if(this.isAuth === false && this.loginPanelActive === false){
        this.loginPanelActive = true
    }
  }

  updateErrorMessageEmail() {
    this.errorMessageEmail = this.email.hasError('required')
      ? 'Debe ingresar un correo'
      : this.email.hasError('email')
        ? 'Correo no válido'
        : '';
  }

  login() {
    const email = this.email.value;
    const password = this.password.value;

    if (email && password) {
      this.authErr = false;
      this.authService.get_token(email, password).subscribe({
        next: (token) => {
          this.authService.login(token.token);
        },
        error: (err) => {
          console.error("Error during login:", err);
          this.authErr = true;
        },
        complete: () =>{
          console.log("Login successfully");
          if(this.nextLink){
            this.router.navigateByUrl(this.nextLink);
          }
        }
      });
    }
  }




}
