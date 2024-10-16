import { Component } from '@angular/core';
import { ActivatedRoute } from '@angular/router';
import { HeaderComponent } from '../../components/header/header.component';
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
    HeaderComponent,
    MatInputModule,
    MatIconModule,
    ReactiveFormsModule,
    MatButtonModule
  ],
  templateUrl: './login.component.html',
  styleUrl: './login.component.css'
})

export class LoginComponent {

  // State variables
  public loginPanelActive:boolean = false;
  public isAuth:boolean = false;
  public nextLink: string | null | undefined;

  // Form variables and error messages
  public email = new FormControl('', [Validators.required, Validators.email]);
  public password = new FormControl('', [Validators.required]);
  public errorMessageEmail = '';

  // State varible to hide or show password
  public hide = true;

  // Authentication error variable
  public authErr = false;

  // Constructor
  constructor(
    private route: ActivatedRoute,
    private router: Router,
    private authService: AuthService) {
      this.email.valueChanges
        .pipe(takeUntilDestroyed())
        .subscribe(() => this.updateErrorMessageEmail());
  }
  ngOnInit(): void {
    this.route.queryParamMap.subscribe(params => {
      this.nextLink = params.get('next');
    });
  }

  // Methods
  public retrieveIsAuth(isAuthD:boolean){
    this.isAuth = isAuthD;
  }

  public showLoginPanel(click:string){
    if(this.isAuth === false && this.loginPanelActive === false){
        this.loginPanelActive = true
    }
  }

  public updateErrorMessageEmail() {
    this.errorMessageEmail = this.email.hasError('required')
      ? 'Debe ingresar un correo'
      : this.email.hasError('email')
        ? 'Correo no válido'
        : '';
  }

  public login() {
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
          }else{
            this.router.navigateByUrl("/apps");
          }
        }
      });
    }
  }

  public registerRedirect(){
    this.router.navigateByUrl("/register");
  }

}
