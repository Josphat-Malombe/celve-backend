


Implementing authentication system
-I am buiding an authentication system where a user logins and can also regster using the third parties such as google and also jwt authentication

-configure django and drf for JWT
-implement register login and logout (refresh) too
store jwt tokens

in settings under installed apps, i set up restframework as well as rest_framework_simplejwt.token_blacklist ....will use it also for logout


set also the default authentication class to 'rest_framework_simplejwt.aunthentication.JWTAuthentication'  also added some simplejwt setting such as token lifetimes and refresh boolean

enabled cors since my frontend will not run on port 8000
