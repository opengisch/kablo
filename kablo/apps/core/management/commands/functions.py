def confirm_reset_data(sys):
    user_input = input("Do you want to reset network data ? [Y/n] : ")
    if user_input.lower() not in {"y", "yes", ""}:
        sys.exit()
