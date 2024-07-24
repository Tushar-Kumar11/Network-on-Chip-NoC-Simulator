def binary_to_decimal(binary_str):
    return int(binary_str, 2)

def break_into_32_bit_chunks(binary_str):
    return [binary_str[i:i+32] for i in range(0, len(binary_str), 32)]

def run():
    with open('Mod_Traffic.txt', 'r') as modified_file:
        modified_data = modified_file.readlines()
    with open('traffic.txt', 'w') as traffic_file:
        for line in modified_data:
            parts = line.strip().split()
            if(len(parts) == 3):
                cycle_number = int(parts[0])
                source_decimal = binary_to_decimal(parts[1])
                destination_decimal = binary_to_decimal(parts[2][:15])
                binary_data = parts[2]
                # print(binary_data)

                for chunk in break_into_32_bit_chunks(binary_data):
                    #print(f"{cycle_number} {source_decimal} {destination_decimal} {chunk}")
                    traffic_file.write(f"{cycle_number} {source_decimal} {destination_decimal} {chunk}\n")
                    cycle_number += 1


if __name__ == '__main__':
    run()