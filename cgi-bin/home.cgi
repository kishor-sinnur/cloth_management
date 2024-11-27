#!"C:/Strawberry/perl/bin/perl.exe"
use strict;
use warnings;
use CGI qw(:standard);
use LWP::UserAgent;
use JSON;

my $cgi = CGI->new;
my $user_agent = LWP::UserAgent->new;

print $cgi->header;

my $user_id = $cgi->param('user_id');

if (!$user_id) {
    print_error_page("User not logged in.");
    exit;
}

if ($cgi->param('action') eq 'add_to_cart') {
    my $book_id = $cgi->param('book_id');

    my $response = $user_agent->post(
        "http://localhost:5000/cart?user_id=$user_id",
        Content       => encode_json({ book_id => $book_id }),
        'Content-Type' => 'application/json'
    );

    if ($response->is_success) {
        print_home_screen("Book added to cart.");
    } else {
        print_home_screen("Failed to add book to cart.");
    }
} else {
    print_home_screen();
}

sub print_home_screen {
    my ($message) = @_;
    print $cgi->start_html(
        -title  => "Home",
        -head   => Link({ -rel => 'stylesheet', -type => 'text/css', -href => '../styles/style.css' })
    );

    # Clean and Minimal Header Section
    print $cgi->div({ -class => 'header' },
        $cgi->div({ -class => 'logo' }, $cgi->h1("MyBookStore")),
        $cgi->div({ -class => 'nav-links' },
            $cgi->a({ -href => 'cart.cgi?user_id=' . $user_id, -class => 'header-link' }, "Go To Cart"),
            $cgi->a({ -href => 'login.cgi', -class => 'header-link' }, "Logout")
        )
    );

    # Main Content

    my $response = $user_agent->get('http://localhost:5000/books');

    if ($response->is_success) {
        my $books = eval { decode_json($response->decoded_content) };
        if ($@) {
            return print_error_page("Failed to parse books data: $@");
        }

        print $cgi->h2("Available Books");
        print $cgi->div({ -class => 'books' },
            map {
                $cgi->div({ -class => 'book-card' },
                    $cgi->img({ -src => $_->{image_url}, -alt => $_->{title}, -class => 'book-image' }),
                    $cgi->div({ -class => 'book-info' },
                        $cgi->p({ -class => 'book-title' }, "Title: $_->{title}"),
                        $cgi->p("Author: $_->{author}"),
                        $cgi->p("Price: $_->{price}"),
                        $cgi->p("Description: $_->{description}")
                    ),
                    $cgi->start_form(-method => 'POST'),
                    $cgi->hidden(-name => 'action', -value => 'add_to_cart'),
                    $cgi->hidden(-name => 'book_id', -value => $_->{id}),
                    $cgi->hidden(-name => 'user_id', -value => $user_id),
                    $cgi->submit(-value => 'Add to Cart', -class => 'btn'),
                    $cgi->end_form
                )
            } @$books
        );

        # Navigation and logout buttons
        
    } else {
        print_error_page("Failed to load books.");
    }

    print $cgi->end_html;
}

sub print_error_page {
    my ($message) = @_;
    print $cgi->start_html(
        -title  => "Error",
        -head   => Link({ -rel => 'stylesheet', -type => 'text/css', -href => '../styles/style.css' })
    );
    print $cgi->div({ -class => 'error' }, $cgi->h1("Error"), $cgi->p($message));
    print $cgi->end_html;
}
