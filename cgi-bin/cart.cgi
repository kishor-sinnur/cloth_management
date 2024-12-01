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

if ($cgi->param('action') eq 'remove_from_cart') {
    my $book_id = $cgi->param('book_id');

    # Ensure both user_id and book_id are provided
    unless ($user_id && $book_id) {
        print_cart_screen("User ID and Book ID are required to remove a book from the cart.");
        return;
    }

    # Make DELETE request
    my $response = $user_agent->delete(
        "http://localhost:5000/cart?user_id=$user_id",
        'Content-Type' => 'application/json',
        Content        => encode_json({ book_id => $book_id })
    );

    if ($response->is_success) {
        print_cart_screen("Book removed from cart.");
    } else {
        my $error_message = $response->decoded_content || "Failed to remove book from cart.";
        print_cart_screen($error_message);
    }
} else {
    print_cart_screen();
}

sub print_cart_screen {
    my ($message) = @_;
    print $cgi->start_html(
        -title  => "Cart",
        -style  => {
            -code => q{
                body {
                    font-family: Arial, sans-serif;
                    margin: 0;
                    padding: 0;
                }
                .header {
                    background-color: #00c853;
                    color: #bdb9b7;
                    padding: 20px;
                    font-size: 24px;
                    text-align: left;
                }
                .header a {
                    color: white;
                    text-decoration: none;
                    float: right;
                    margin-right: 20px;
                    font-size: 16px;
                }
                .cart-item {
                    display: flex;
                    align-items: center;
                    justify-content: space-between;
                    padding: 15px;
                    margin: 10px;
                    border: 1px solid #ddd;
                    border-radius: 10px;
                    background-color: #fff;
                }
                .cart-item img {
                    width: 50px;
                    height: 70px;
                    border-radius: 5px;
                }
                .cart-item div {
                    flex: 1;
                    margin-left: 15px;
                }
                .cart-item button {
                    background-color: #ff1744;
                    color: white;
                    border: none;
                    padding: 10px;
                    border-radius: 5px;
                    cursor: pointer;
                }
                .cart-item button:hover {
                    background-color: #d50000;
                }
                .footer {
                    background-color: #2962ff;
                    color: white;
                    text-align: center;
                    padding: 20px;
                    font-size: 18px;
                }
                .message {
                    text-align: center;
                    margin: 20px 0;
                    font-size: 16px;
                    color: #333;
                }
            }
        }
    );

    print '<div class="header">Cart <a href="home.cgi?user_id=' . $user_id . '">Back to home</a></div>';
    print '<div class="message">' . $cgi->escapeHTML($message) . '</div>' if $message;

    my $response = $user_agent->get("http://localhost:5000/cart?user_id=$user_id");

    if ($response->is_success) {
        my $cart_items = eval { decode_json($response->decoded_content) };
        if ($@) {
            return print_error_page("Failed to parse cart data: $@");
        }

        my $total_price = 0;  # Initialize total price

        foreach my $item (@$cart_items) {
            $total_price += $item->{price};  # Add each book's price to the total

            print qq{
                <div class="cart-item">
                    <img src="$item->{image_url}" alt="$item->{title}">
                    <div>
                        <p><strong>$item->{title}</strong></p>
                        <p>$item->{price}</p>
                    </div>
                    <form method="POST">
                        <input type="hidden" name="action" value="remove_from_cart">
                        <input type="hidden" name="book_id" value="$item->{book_id}">
                        <input type="hidden" name="user_id" value="$user_id">
                        <button type="submit">REMOVE</button>
                    </form>
                </div>
            };
        }

        # Display the calculated total price in the footer
        print qq{
            <div class="footer">Total: $total_price</div>
        };
    } else {
        print_error_page("Failed to load cart.");
    }

    print $cgi->end_html;
}
