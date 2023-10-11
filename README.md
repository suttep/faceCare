# FaceCare a Skin Cycling Planner
#### Video Demo:  https://www.youtube.com/watch?v=g8pIo9McEuU
#### Description:
FaceCare is an application inspired by the rising topic of skin cycling in social media. Many people still doesn't know how to do skin cycling correct. This application will help people plan and track skin cycling routines based on their skin condition. FaceCare will help its user by generating a skincare buying guide and plan a personalized skin cycling routine. User also able to modify their skin cycling routines and maybe if their skin condition changed, they able to modify their skin condition and generate new skin cycle plan.

#### Features:
This application uses Flask web framework based in python and the page is made using HTML and css with the help of bootstrap.

#### Explanation:
1. For starter user will be asked to register or login.
2. Application will save the user inputted data (email, name, password, and face condition)
3. The application will then bring you to the homepage that display the current day skin cycle based on the user face condition.
4. User can access to the skincare guide. The application will display skincare buying guide based on the user face condition.
5. User can track their skin cycle routine by accessing the monthly skincycle page.
6. User can only log for today skincycle to avoid cheating.
7. To log, user click the "Log Today" button in home page.
8. User can change their skin cycle plan on the customize skincycle page.
9. User also can change their face condition on the account page.

#### How the application works:
1. Create and Track Skin Cycle
    - For the application to track and produce skin cycle. The application when user create an account it will automatically create a starting date.
    - The application will get today date and the starting date.
    - The application decide if the day is greater or lower than starting date.
    - Using the ".days" it will receive the range of days from starting date to the target date.
    - Using modulo of 4 or the '% 4'. it will either produce [3, 2, 1, 0].
    - Using the generated array the system will display the correct skin cycle routine.

2. Creating Custom Skin Cycling Routine
    - The user can create a customized skin cycle routine based on their preference.
    - The system by default didn't save any custom skin cycle routine. it was generated everytime user access the application based on the current face condition.
    - If the user decided to create a custom skin cycle. then the application will just save it and then change the array to the now customized skin cycle.