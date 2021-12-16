import React from 'react';
import { AmplifySignIn, AmplifyAuthenticator, AmplifySignUp } from '@aws-amplify/ui-react';
import Amplify, { Auth } from 'aws-amplify';
import awsmobile from './aws-exports';
import { AuthState, onAuthUIStateChange } from '@aws-amplify/ui-components';
import './App.css';
import Analytics from './Analytics'
import Upload from './Upload'

// Load awsconfig_cognito pools to the Amplify and Auth modules
Amplify.configure(awsmobile);
Auth.configure(awsmobile);

  //Signout from the NCI App
  async function ampSignOut() {
    try {
        await Auth.signOut({ global:true });;
        await new Promise(res => setTimeout(res, 1));
        window.location.reload();  //Reload Window

    } catch (error) {
        console.log('Signout Error: ', error);
    }
  }

// Ref AWS Amplify Custom Authenticator
// https://docs.amplify.aws/ui/auth/authenticator/q/framework/react/
const AuthApp = () => {

  const [currentView, setCurrentView] = React.useState("Analytics");

  const [authStateInfo, setAuthState] = React.useState();
  const [userData, setUser] = React.useState();

  // Ref Authenticator Usage
  // https://docs.amplify.aws/ui/auth/authenticator/q/framework/react/#basic-usage
  React.useEffect(() => {
      return onAuthUIStateChange((nextAuthState, authData) => {
          setAuthState(nextAuthState);
          setUser(authData)
      });
  }, []);

  function getUserName(user){
    return (user.signInUserSession ? user.attributes.given_name : user.username)
  }

  return authStateInfo === AuthState.SignedIn && userData ? (
    <div className="App">
        <div href="#analytics" className="App-header">&nbsp;&nbsp;NCI Attendance&nbsp;&nbsp;</div>
        <button onClick={ampSignOut} className="App-logout">&nbsp;&nbsp;Sign Out&nbsp;&nbsp;</button>
        <div className="App-first"><h3>Hello, {getUserName(userData)} </h3></div>
        {
          currentView === "Analytics" ? 
          <Analytics email={userData.attributes.email} onClick={page => setCurrentView(page)} /> : 
          <Upload email={userData.attributes.email} onClick={page => setCurrentView(page)} />
        }
    </div>
  ) : (
    // AmplifyAuthenticator to Register
    <AmplifyAuthenticator usernameAlias="email">
        <AmplifySignUp
          slot="sign-up"
          headerText="Create a new account"
          className="App" 
          style={{
            display: 'flex',
            alignItems: 'center',
            borderRadius: 10,
            height: '100vh',
            backgroundColor: 'powderblue'
          }}
          usernameAlias="email"
          formFields={[
            {
              type: "given_name",
              label: "First Name",
              placeholder: "First Name",
              required: true
            },
            {
              type: "family_name",
              label: "Last Name",
              placeholder: "Last Name",
              required: true
            },
            { 
              type: "email" 
            },
            { 
              type: "password" 
            }
          ]}
        />
        <div className="App" slot="sign-in" style={{
          display: 'flex',
          alignItems: 'center',
          borderRadius: 10,
          height: '100vh',
          backgroundColor: 'powderblue'
        }} >
        <div className="App-header-login"><p>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;NCI Attendance&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;</p>
          <AmplifySignIn slot="sign-in" usernameAlias="email" />
        </div>
        </div>
      </AmplifyAuthenticator>
);

}

export default AuthApp;
