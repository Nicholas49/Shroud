# These are just some simple functions used repeatedly throughout the program to avoid having the same print statements
# repeated over and over
# Only a couple actually return anything


def choose_contact(youser):

    # Prints out a list of the contacts in the passed in user's contact_list
    # Each is preceded by a number for the user to easily select the contact and return it as a dictionary
    # If no valid option is picked and the user opts not to retry it returns the boolean value 'False'

    while True:
        print("Select Contact")
        br()

        # Printing the names

        num = 1
        for cname in youser.contactlist:
            print(str(num) + ": " + cname['name'])
            num += 1

        # Getting the selection and checking if it's a valid choice

        selection = input("> ")
        snumb = int(selection) - 1

        if 0 <= snumb < len(youser.contactlist):
            return youser.contactlist[snumb]
        else:
            badinput(str(len(youser.contactlist)))
            if goback():
                return False


def badinput(num):

    # For whenever the user is given a list of options and they enter a number not on said list
    # Tells them to enter a number within the given range passed in

    print("Not a valid entry.")
    if num == "2":
        print("Enter 1 or 2.")
    else:
        print("Enter a number (1 - " + num + ")")


def goback():

    # For whenever user gives a bad input
    # If False is returned the outer loop will generally repeat
    # If True is returned the outer loop will either break or end

    while True:
        print("")
        print("1: Try again")
        print("2: Return")
        choice = input("> ")
        if choice == "1":
            return False
        elif choice == "2":
            return True
        badinput("2")


def continu():

    # This provides a general purpose break for the user to view and/or copy printed info before returning
    # To the previous menu

    br()
    input("Press Enter to continue.")


def br(numb=1):

    # Spacing out text improves readability.
    # This saves me from repeatedly typing 'print("")' all the time

    numb = int(numb)
    for i in range(numb):
        print("")
