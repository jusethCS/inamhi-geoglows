import {Component} from '@angular/core';
import {Router} from '@angular/router';
import {MatInputModule} from '@angular/material/input';
import {MatIconModule} from '@angular/material/icon';
import {MatButtonModule} from '@angular/material/button';
import {takeUntilDestroyed} from '@angular/core/rxjs-interop';
import {FormControl, Validators, FormsModule, ReactiveFormsModule} from '@angular/forms';
import { AuthService } from '../../services/auth.service';
import { HeaderComponent } from "../../components/header/header.component";

@Component({
  selector: 'app-register',
  standalone: true,
  imports: [
    MatInputModule,
    MatIconModule,
    MatButtonModule,
    FormsModule,
    ReactiveFormsModule,
    HeaderComponent
],
  templateUrl: './register.component.html',
  styleUrl: './register.component.css'
})

export class RegisterComponent {

  // Form variables and error messages
  public pattern = "^[a-zA-Z0-9._%+-]+@(?!.*\.com$)[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
  public email = new FormControl('', [Validators.required, Validators.email,Validators.pattern(this.pattern)]);
  public password = new FormControl('', [Validators.required]);
  public firstname = new FormControl('', [Validators.required]);
  public lastname = new FormControl('', [Validators.required]);
  public institution = new FormControl('', [Validators.required]);
  public position = new FormControl('', [Validators.required]);

  public errorMessageEmail = '';
  public loginPanelActive:boolean = false;
  public isAuth:boolean = false;
  public hide = true;

  // Constructor
  constructor(private router: Router, private authService: AuthService) {
    this.email.valueChanges
      .pipe(takeUntilDestroyed())
      .subscribe(() => this.updateErrorMessageEmail());
  }

  public retrieveIsAuth(isAuthD:boolean){
    this.isAuth = isAuthD;
  }

  public showLoginPanel(click:string){
    if(this.isAuth === false && this.loginPanelActive === false){
        this.loginPanelActive = true
    }
  }

  // Update status and erros in form values
  public updateErrorMessageEmail() {
    switch(true) {
      case this.email.hasError('required'):
        this.errorMessageEmail = 'Debe ingresar un correo';
        break;
      case this.email.hasError('email'):
        this.errorMessageEmail = 'Correo no válido';
        break;
      case this.email.hasError('pattern'):
        this.errorMessageEmail = 'Debe ingresar un correo institucional';
        break;
      default:
        this.errorMessageEmail = '';
    }
}

  // Institutional email validator
  public institutionalEmail(control: FormControl) {
    const valor = control.value as string;
    if (valor && valor.toLowerCase().endsWith('.com')) {
      return { 'commail': true };
    }
    return null;
  }

  // Show the login form (user authentication)
  public redirectToLogin() {
    this.router.navigateByUrl('/');
  }

  // Register new user into database
  public register(): void{
    const data =  {
      email: this.email.value,
      pass: this.password.value,
      firstname: this.firstname.value,
      lastname: this.lastname.value,
      institution: this.institution.value,
      position: this.position.value
    }
    this.authService.register_user(data).subscribe({
      next: (response) => {
        if (response.status == "success") {
          alert("Usuario ingresado correctamente.")
          window.location.reload();
        }else{
          alert("No se pudo registrar al usuario. Intente de nuevo.")
        }
      },
      error: (err) => {
        alert("El servidor no pudo procesar su solicitud.")
      }
    })
  }
}
