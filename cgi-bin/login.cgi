#!"C:/Strawberry/perl/bin/perl.exe"
use strict;
use warnings;
use CGI qw(:standard);
use LWP::UserAgent;
use JSON;

my $cgi = CGI->new;
my $user_agent = LWP::UserAgent->new;

if ($cgi->param('action') eq 'login') {
    my $username = $cgi->param('username');
    my $password = $cgi->param('password');

    my $response = $user_agent->post(
        'http://localhost:5000/login',
        Content       => encode_json({ username => $username, password => $password }),
        'Content-Type' => 'application/json'
    );

    if ($response->is_success) {
        my $data = eval { decode_json($response->decoded_content) };
        if ($@ || !$data->{user_id}) {
            print_error_page("Failed to parse login response: $@");
        } else {
            # Redirect based on user_id
            if ($data->{user_id} == 1) {
                print $cgi->redirect(-uri => "admin.cgi"); # Redirect to admin page
            } else {
                print $cgi->redirect(-uri => "home.cgi?user_id=$data->{user_id}");
            }
            exit;
        }
    } else {
        print_error_page("Login Failed: Invalid credentials.");
    }
} else {
    print_login_form();
}

sub print_login_form {
    print $cgi->header;
    print $cgi->start_html(
        -title  => 'Login',
        -style  => {
            -code => q{
                body {
                font-family: "Roboto", sans-serif;
                text-align: center;
                margin: 0;
                padding: 0;
                background: linear-gradient(135deg, #1184ee, #6900ff, #9face6);
                height: 100vh;
                display: flex;
                justify-content: center;
                align-items: center;
            }
            .container {
                max-width: 400px;
                width: 90%;
                background: white;
                padding: 30px;
                box-shadow: 0 8px 16px rgba(0, 0, 0, 0.2);
                border-radius: 12px;
                text-align: left;
            }
            .container h1 {
                margin-bottom: 20px;
                color: #333;
                font-size: 24px;
                text-align: center;
            }
            input[type="text"], input[type="password"] {
                width: 100%;
                padding: 10px;
                margin: 10px 0;
                border: 1px solid #ddd;
                border-radius: 8px;
                font-size: 16px;
            }
            input[type="submit"] {
                width: 100%;
                padding: 12px;
                margin-top: 15px;
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
            .register-link {
                text-align: center;
                margin-top: 20px;
                font-size: 14px;
                color: #333;
            }
            .register-link a {
                text-decoration: none;
                color: #0056b3;
                font-weight: bold;
            }
            .register-link a:hover {
                text-decoration: underline;
            }
        }
    }
        
    );

    print $cgi->div(
        { -class => 'container' },
        $cgi->h1('Welcome Back!'),
        $cgi->start_form(-method => 'POST'),
        $cgi->textfield(
            -name        => 'username',
            -placeholder => 'Enter your username',
            -required    => 'required'
        ),
        $cgi->password_field(
            -name        => 'password',
            -placeholder => 'Enter your password',
            -required    => 'required'
        ),
        $cgi->hidden(-name => 'action', -value => 'login'),
        $cgi->submit(-value => 'Login'),
        $cgi->div(
            { -class => 'register-link' },
            "Don't have an account? ",
            $cgi->a({ -href => 'register.cgi' }, 'Register Here')
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
        $cgi->a({ -href => 'login.cgi' }, 'Go back to Login')
    );

    print $cgi->end_html;
}
