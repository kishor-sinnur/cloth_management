#!"C:/Strawberry/perl/bin/perl.exe"

use strict;
use warnings;
use CGI qw(:standard);
use LWP::UserAgent;
use JSON;
use File::Basename;
use File::Copy;

# Create a new CGI object
my $cgi = CGI->new;

# Print the HTTP header
print $cgi->header;

# Define the image storage path (use an absolute path for reliability)
my $image_storage_path = 'C:/xampp/htdocs/static/images';

# If the form is submitted
if ($cgi->param('addbook')) {
    # Get form parameters
    my $title       = $cgi->param('title') || '';
    my $author      = $cgi->param('author') || '';
    my $price       = $cgi->param('price') || '';
    my $description = $cgi->param('description') || '';
    my $image       = $cgi->upload('image');

    my $image_url;

    # Save the uploaded image to the specified directory
    if ($image) {
        # Extract and sanitize the filename
        my $filename = $cgi->param('image');
        $filename = basename($filename);

        # Construct the target file path
        my $target_file = "$image_storage_path/$filename";

        # Ensure the target directory exists
        unless (-d $image_storage_path) {
            mkdir $image_storage_path or die "Could not create directory: $image_storage_path - $!";
        }

        # Save the file
        open(my $out, '>', $target_file) or die "Cannot open $target_file for writing: $!";
        binmode $out;

        # Read and save the uploaded file data
        while (my $buffer = <$image>) {
            print $out $buffer;
        }
        close $out;

        # Set the image URL for form submission
        $image_url = "../static/images/$filename";
    }

    # Validate required fields
    unless ($title && $author && $price && $description) {
        print_error_page("All fields except the image are required.");
        exit;
    }

    # Create a UserAgent object
    my $ua = LWP::UserAgent->new;

    # Prepare the POST request
    my $url = 'http://127.0.0.1:5000/addbooks';
    my $response = $ua->post(
        $url,
        Content_Type => 'form-data',
        Content      => [
            title       => $title,
            author      => $author,
            price       => $price,
            description => $description,
            image_url   => $image_url || '',
        ]
    );

    # Process the response
    if ($response->is_success) {
        print_success_page("Book added successfully!");
    } else {
        print_error_page("Error: " . $response->decoded_content);
    }
} else {
    print_form_page();
}

# Subroutine to display the form
sub print_form_page {
    print $cgi->start_html(
        -title => 'Add Book',
        -style => {
            code => q{
            body {
                font-family: Arial, sans-serif;
                background: #c60cf3;
                margin: 0;
                padding: 0;
                display: flex;
                justify-content: center;
                align-items: center;
                height: 100vh;
            }
            .container {
                background: #fff;
                padding: 20px 30px;
                border-radius: 8px;
                box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
                width: 400px;
            }
            h1 {
                text-align: center;
                color: #333;
                margin-bottom: 20px;
            }
            p {
                font-size: 14px;
                color: #555;
                margin-bottom: 10px;
            }
            input[type="text"], input[type="file"], input[type="submit"], textarea {
                width: 100%;
                padding: 10px;
                margin: 10px 0;
                border: 1px solid #ddd;
                border-radius: 6px;
                font-size: 14px;
            }
            input[type="submit"] {
                background: #007BFF;
                color: #fff;
                cursor: pointer;
                transition: background 0.3s ease;
            }
            input[type="submit"]:hover {
                background: #0056b3;
            }
            }
        }
    );

    print $cgi->div(
        { -class => 'container' },
        $cgi->h1("Add a New Book"),
        $cgi->p("Fill in the details below and upload an optional book image."),
        $cgi->start_form(
            -method  => 'POST',
            -action  => 'admin.cgi',
            -enctype => 'multipart/form-data'
        ),
        $cgi->textfield(-name => 'title', -placeholder => 'Book Title'),
        $cgi->textfield(-name => 'author', -placeholder => 'Author'),
        $cgi->textfield(-name => 'price', -placeholder => 'Price (e.g., 9.99)'),
        $cgi->textarea(-name => 'description', -placeholder => 'Description', -rows => 5),
        $cgi->filefield(-name => 'image', -accept => 'image/*'),
        $cgi->submit(-name => 'addbook', -value => 'Add Book'),
        $cgi->end_form
    );

    print $cgi->end_html;
}

# Subroutine to display success message with navigation buttons
sub print_success_page {
    my ($message) = @_;
    print $cgi->start_html(
        -title => 'Success',
        -style => {
            code => q{
            body {
                font-family: Arial, sans-serif;
                background: #d4edda;
                margin: 0;
                padding: 0;
                display: flex;
                justify-content: center;
                align-items: center;
                height: 100vh;
            }
            .success-box {
                background: white;
                padding: 20px 30px;
                border-radius: 8px;
                text-align: center;
                box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
            }
            h1 {
                color: #155724;
                font-size: 18px;
                margin-bottom: 10px;
            }
            a.button {
                display: inline-block;
                margin: 10px 5px;
                padding: 10px 20px;
                color: white;
                background: #007BFF;
                text-decoration: none;
                border-radius: 5px;
                font-size: 14px;
            }
            a.button:hover {
                background: #0056b3;
            }
            }
        }
    );

    print $cgi->div(
        { -class => 'success-box' },
        $cgi->h1($cgi->escapeHTML($message)),
        $cgi->a({ -href => 'home.cgi?user_id=1', -class => 'button' }, 'Go to Home'),
        $cgi->a({ -href => 'admin.cgi', -class => 'button' }, 'Add More Books')
    );

    print $cgi->end_html;
}

# Subroutine to display error message with navigation buttons
sub print_error_page {
    my ($message) = @_;
    print $cgi->start_html(
        -title => 'Error',
        -style => {
            code => q{
            body {
                font-family: Arial, sans-serif;
                background: #f8d7da;
                margin: 0;
                padding: 0;
                display: flex;
                justify-content: center;
                align-items: center;
                height: 100vh;
            }
            .error-box {
                background: white;
                padding: 20px 30px;
                border-radius: 8px;
                text-align: center;
                box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
            }
            h1 {
                color: #721c24;
                font-size: 18px;
                margin-bottom: 10px;
            }
            a.button {
                display: inline-block;
                margin: 10px 5px;
                padding: 10px 20px;
                color: white;
                background: #007BFF;
                text-decoration: none;
                border-radius: 5px;
                font-size: 14px;
            }
            a.button:hover {
                background: #0056b3;
            }
            }
        }
    );

    print $cgi->div(
        { -class => 'error-box' },
        $cgi->h1($cgi->escapeHTML($message)),
        $cgi->a({ -href => 'home.cgi?user_id=1', -class => 'button' }, 'Go to Home'),
        $cgi->a({ -href => 'admin.cgi', -class => 'button' }, 'Add More Books')
    );

    print $cgi->end_html;
}
