#!"C:/Strawberry/perl/bin/perl.exe"
use strict;
use warnings;
use CGI qw(:standard);
use LWP::UserAgent;
use JSON;

my $cgi = CGI->new;

if ($cgi->param('register')) {
    my $username = $cgi->param('username');
    my $password = $cgi->param('password');

    # Create a new UserAgent object
    my $ua = LWP::UserAgent->new;
    my $response = $ua->post(
        'http://127.0.0.1:5000/register',
        Content       => encode_json({ username => $username, password => $password }),
        'Content-Type' => 'application/json'
    );

    if ($response->is_success) {
        # Redirect to login.cgi on successful registration
        print $cgi->redirect('login.cgi');
        exit;
    } else {
        print_error_page("Registration Failed: " . $response->decoded_content);
    }
} else {
    print_registration_form();
}

sub print_registration_form {
    print $cgi->header;
    print $cgi->start_html(
        -title  => 'Register',
        -style  => {
            code => q{
            body {
                font-family: "Roboto", sans-serif;
                background: linear-gradient(135deg, #ff9a9e, #fad0c4);
                height: 100vh;
                margin: 0;
                display: flex;
                justify-content: center;
                align-items: center;
            }
            .container {
                background: white;
                padding: 30px;
                border-radius: 12px;
                box-shadow: 0 8px 16px rgba(0, 0, 0, 0.2);
                max-width: 400px;
                width: 90%;
                text-align: center;
            }
            .container h1 {
                margin-bottom: 20px;
                color: #333;
                font-size: 24px;
            }
            input[type="text"], input[type="password"] {
                width: 100%;
                padding: 12px;
                margin: 10px 0;
                border: 1px solid #ddd;
                border-radius: 8px;
                font-size: 16px;
            }
            input[type="submit"] {
                width: 100%;
                padding: 12px;
                background-color: #5cb85c;
                color: white;
                border: none;
                border-radius: 8px;
                font-size: 16px;
                cursor: pointer;
                transition: background-color 0.3s;
            }
            input[type="submit"]:hover {
                background-color: #4cae4c;
            }
            .login-link {
                margin-top: 20px;
                font-size: 14px;
                color: #333;
            }
            .login-link a {
                text-decoration: none;
                color: #0056b3;
                font-weight: bold;
            }
            .login-link a:hover {
                text-decoration: underline;
            }
            }}
    );

    print $cgi->div(
        { -class => 'container' },
        $cgi->h1('Create an Account'),
        $cgi->start_form(-method => 'POST', -action => 'register.cgi'),
        $cgi->textfield(-name => 'username', -placeholder => 'Username', -required => 'required'),
        $cgi->password_field(-name => 'password', -placeholder => 'Password', -required => 'required'),
        $cgi->submit(-name => 'register', -value => 'Register'),
        $cgi->div(
            { -class => 'login-link' },
            "Already have an account? ",
            $cgi->a({ -href => 'login.cgi' }, 'Login Here')
        ),
        $cgi->end_form
    );

    print $cgi->end_html;
}

sub print_error_page {
    my ($message) = @_;
    print $cgi->header;
    print $cgi->start_html(
        -title => 'Error',
        -style => {
            code => q{
          
            body {
                font-family: "Roboto", sans-serif;
                background-color: #f8d7da;
                text-align: center;
                color: #721c24;
                margin: 0;
                padding: 50px 20px;
            }
            .error-box {
                max-width: 600px;
                margin: auto;
                background: white;
                padding: 20px;
                border: 1px solid #f5c6cb;
                border-radius: 10px;
                box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
            }
            .error-box h1 {
                color: #721c24;
                font-size: 22px;
                margin-bottom: 10px;
            }
            .error-box p {
                color: #555;
                font-size: 16px;
            }
            .error-box a {
                text-decoration: none;
                color: #0056b3;
                font-size: 16px;
                margin-top: 15px;
                display: inline-block;
            }
            .error-box a:hover {
                text-decoration: underline;
            }
            }}
    );

    print $cgi->div(
        { -class => 'error-box' },
        $cgi->h1('Oops! Something went wrong.'),
        $cgi->p($cgi->escapeHTML($message)),
        $cgi->a({ -href => 'register.cgi' }, 'Try Again')
    );

    print $cgi->end_html;
}
