import txt_Converter as conv
import sys
import random
import matplotlib.pyplot as plt
import numpy as np


try:    
    algo = int(input("Choose 0 for XY Algo and 1 for YX Algo: "))  # 0 for xy | 1 for yx
    run_mode = int(input("Choose 0 for PVA Algo and 1 for PVS Algo: "))  # 0 for PVA | 1 for PVS
    with open('Report.txt', 'w') as report_file:
        pass
    with open('Log_File.txt', 'w') as output_file:
        sys.stdout = output_file
        class Router:
            def __init__(self,router_id,bd,sd,cd):
                self.router_id = router_id
                self.input_buffer = []
                self.crossbar = []
                self.switch_allocator = []
                self.buffer_delay = bd
                self.switch_allocator_delay = sd
                self.crossbar_delay = cd
                self.processing_element = 0
                self.timePassed_switch_allocator=0.0
                self.timePassed_buffer=0.0
                self.timePassed_crossbar=0.0

            def isempty(self):
                if((len(self.input_buffer) == 0) and (len(self.switch_allocator) == 0) and (len(self.crossbar) == 0)):
                    return True
                return False

            def __str__(self):
                s = ""
                s += f"Router ID : {self.router_id} \n"
                if(self.input_buffer != []):
                    s += f"Input Buffer Value : {self.input_buffer} \n"
                if(self.input_buffer == []):
                    s += f"Input Buffer Value : None \n"
                if(self.switch_allocator != []):
                    s += f"Switch Allocator Value : {self.switch_allocator} \n"
                if(self.switch_allocator == []):
                    s += f"Switch Allocator Value : None \n"
                if(self.crossbar != []):
                    s += f"CrossBar Value : {self.crossbar} \n"
                if(self.crossbar == []):
                    s += f"CrossBar Value : None \n"
                return s

            def inject(self,flit_details):
                self.input_buffer.append(flit_details)
                self.processing_element += 1

            def receive(self,period,received_flits,clock,delayed_list):
                if(self.crossbar != []):
                    self.timePassed_crossbar+=period
                    if((self.crossbar_delay>self.timePassed_crossbar)): #drop
                        val = self.crossbar[0]
                        delayed_list.append([clock,self.router_id,2,val])

                    else:
                        val = self.crossbar.pop(0)
                        val[4] += self.timePassed_crossbar
                        self.processing_element += 1
                        received_flits.append(val)
                        self.timePassed_crossbar=0

                if(self.switch_allocator != []):
                    self.timePassed_switch_allocator+=period
                    if((self.switch_allocator_delay>self.timePassed_switch_allocator) or len(self.crossbar)!=0): #drop
                        val = self.switch_allocator[0]
                        delayed_list.append([clock,self.router_id,1,val])

                    else:
                        val = self.switch_allocator.pop(0)
                        val[4] += self.timePassed_switch_allocator
                        self.crossbar.append(val)
                        self.timePassed_switch_allocator=0

                if(self.input_buffer != []):
                    self.timePassed_buffer+=period
                    if((self.buffer_delay>self.timePassed_buffer) or len(self.switch_allocator)!=0): #drop
                        val = self.input_buffer[0]
                        delayed_list.append([clock,self.router_id,0,val])

                    else:
                        val = self.input_buffer.pop(0)
                        val[4] += self.timePassed_buffer
                        self.switch_allocator.append(val)
                        self.timePassed_buffer=0

            def is_ready_to_receive(self,des):
                if(int(self.router_id) == int(des) and self.crossbar != []):
                    return True
                return False

            def getflit(self): #returns flit details
                if(self.crossbar != []):
                    return self.crossbar[0]
                if(self.switch_allocator != []):
                    return self.switch_allocator[0]
                if(self.input_buffer != []):
                    return self.input_buffer[0]

            def update(self,next_id,allrouter,period,links,clock,delayed_list):
                nextrouter = allrouter[next_id]
                if(len(self.crossbar) != 0):
                    self.timePassed_crossbar+=period
                    if((self.crossbar_delay>self.timePassed_crossbar)): #drop
                        val = self.crossbar[0]
                        delayed_list.append([clock,self.router_id,2,val])

                    else:
                        val = self.crossbar.pop(0)
                        val[4] += self.timePassed_crossbar #delay
                        nextrouter.input_buffer.append(val)
                        s = str(self.router_id) + str(nextrouter.router_id)
                        s = ''.join(sorted(s))
                        links[s] += 1
                        self.timePassed_crossbar=0
                    
                if(len(self.switch_allocator) != 0):
                    self.timePassed_switch_allocator+=period
                    if((self.switch_allocator_delay>self.timePassed_switch_allocator) or len(self.crossbar)!=0): #drop
                        val = self.switch_allocator[0]
                        delayed_list.append([clock,self.router_id,1,val])

                    else:
                        val = self.switch_allocator.pop(0)
                        val[4] += self.timePassed_switch_allocator #delay
                        self.crossbar.append(val)
                        self.timePassed_switch_allocator=0

                if(len(self.input_buffer) != 0):
                    self.timePassed_buffer+=period
                    if((self.buffer_delay>self.timePassed_buffer) or len(self.switch_allocator)!=0): #drop
                        val = self.input_buffer[0]
                        delayed_list.append([clock,self.router_id,0,val])

                    else :
                        val = self.input_buffer.pop(0)
                        val[4] += self.timePassed_buffer #delay
                        self.switch_allocator.append(val)
                        self.timePassed_buffer=0

            def is_destination_flit(self,des):
                if(self.router_id == int(des)):
                    return True
                return False

        if __name__ == '__main__':

            def decode_flit_type(flit):
                last_two_bits = flit[-2:]
                if last_two_bits == "01":
                    return "Body Flit"
                elif last_two_bits == "00":
                    return "Head Flit"
                elif last_two_bits == "10":
                    return "Tail Flit"
                else:
                    return "Unknown Flit Type"
            def decode_PE_type(last_two_bits):
                # last_two_bits = flit[-2:]
                if last_two_bits == 0:
                    return "Input_Buffer"
                elif last_two_bits == 1:
                    return "Switch Allocator"
                elif last_two_bits == 2:
                    return "Crossbar"
                else:
                    return "Unknown Flit Type"

            def generate_gaussian_delays(mean, std_dev, count,run_mode):
                if(run_mode == 0 ):
                    return [float(mean) for _ in range(count)]
                return [random.gauss(mean, std_dev) for _ in range(count)]
            
            def xy1(flit_details,curr):
                dest=int(flit_details[2])
                curr_row=curr//3
                dest_row=dest//3
                curr_col=curr%3
                dest_col=dest%3
                next_id=0
                if(curr_col==dest_col):
                    if(curr_row==dest_row):
                        next_id= dest
                    elif(curr_row<dest_row):
                        next_id= (curr+3)
                    else:
                        next_id= (curr-3)
                else:
                    if(curr_col<dest_col):
                        next_id= (curr+1)
                    else:
                        next_id= curr-1
                        
                return next_id
            
            def yx1(flit_details,curr):
                dest = int(flit_details[2])
                curr_row = curr // 3
                dest_row = dest // 3
                curr_col = curr % 3
                dest_col = dest % 3
                next_id = 0

                # First, move along the Y-axis
                if curr_row < dest_row:
                    next_id = (curr + 3)
                elif curr_row > dest_row:
                    next_id = (curr - 3)
                else:
                    # If rows are the same, move along the X-axis
                    if curr_col < dest_col:
                        next_id = (curr + 1)
                    elif curr_col > dest_col:
                        next_id = (curr - 1)
                    else:
                        # If both rows and columns are the same, stay in the current router
                        next_id = curr

                return next_id
            
            def total_cycles_taken(all_routers,flit_details,algo):
                curr_router = all_routers[int(flit_details[0])]
                des_router = all_routers[int(flit_details[1])]
                cnt = 3
                while(curr_router != des_router):
                    curr = int(curr_router.router_id)
                    next_id = int(xy1(flit_details,curr)) if (algo == 0) else int(yx1(flit_details,curr))
                    curr_router = all_routers[next_id]
                    cnt += 3
                return cnt
            
            def ispresent(clock,traffic_file):
                for i in range(0,len(traffic_file)):
                    if(clock == int(traffic_file[i][0])):
                        return traffic_file[i]
                    
                return []
            
            def all_empty(all_routers):
                i = 0
                while(i < len(all_routers)):
                    if(not all_routers[i].isempty()):
                        return False
                    
                    i += 1

                return True
            
            def is_valid_flit_type(flit):
                if len(flit) != 32:
                    print("Length of Flits is not 32")
                    return False
                
                return all(bit in '01' for bit in flit)
            
            def bubble_sort(lst,n):
                for i in range(n):
                    for j in range(n-i-1):
                        if int(lst[j][0]) > int(lst[j+1][0]):
                            lst[j], lst[j+1] = lst[j+1], lst[j]

            def check_last_two_digits(temp1, temp2):
                return temp1[3][-2:] == temp2[3][-2:]

            def link_graph(dic1, dic2):
                x1_values = list(dic1.keys())
                y1_values = list(dic1.values())
                
                x2_values = list(dic2.keys())
                y2_values = list(dic2.values())

                fig, axs = plt.subplots(1, 2, figsize=(12, 4.5))

                axs[0].bar(x1_values, y1_values)
                axs[0].set_ylabel("Flits Sent")
                axs[0].set_title("Graph of Links vs flits sent")
                axs[0].set_xticks(range(len(x1_values)))
                axs[0].set_xticklabels(x1_values, rotation=45, ha='right')  # Rotate labels for better visibility
                axs[0].tick_params(axis='x', which='major', pad=5)  # Adjust padding between ticks and labels
                axs[0].set_xlabel("Links", labelpad=7)

                axs[1].bar(x2_values, y2_values)
                axs[1].set_xlabel("Router ID")
                axs[1].set_ylabel("Flit Updates")
                axs[1].set_title("PE Flits")
                plt.xticks(range(len(x2_values)), x2_values)

                fig.tight_layout()
                plt.savefig("Graph1.png")
                plt.show()

            def graph2(traffic_file,received_flits):
                x = []
                y = []
                head = 1
                body = 1
                tail = 1
                for i in range(0,len(traffic_file)):
                    for j in range(0,len(received_flits)):
                        if(traffic_file[i][0:4] == received_flits[j][0:4]):
                            flit_type = decode_flit_type(traffic_file[i][3])
                            if(flit_type == "Head Flit"):
                                x.append(flit_type + str(head))
                                y.append(received_flits[j][4])
                                head += 1
                                received_flits.pop(j)
                                break
                            elif(flit_type == "Body Flit"):
                                x.append(flit_type + str(body))
                                y.append(received_flits[j][4])
                                body += 1
                                received_flits.pop(j)
                                break
                            elif(flit_type == "Tail Flit"):
                                x.append(flit_type + str(tail))
                                y.append(received_flits[j][4])
                                tail += 1
                                received_flits.pop(j)
                                break
                f = plt.figure()
                plt.bar(x, y)
                plt.xlabel('Flit Type')
                plt.ylabel('Received Flits')
                plt.title('Bar Graph of Received Flits')
                for i, value in enumerate(y):
                    plt.text(i, value + 0.1, str(value), ha='center', va='bottom')
                plt.yticks(np.arange(0, max(y)+1, 2))
                plt.savefig("Graph2.png")
                plt.show()

            try:
                flagSarva = 0
                conv.run()
                with open('traffic.txt', 'r') as file:
                    lines = file.readlines()
                    eachline2 = []
                    line_number = 1  

                    for i in range(0, len(lines), 3):
                        temp1 = lines[i].strip().split()
                        temp2 = lines[i + 1].strip().split()
                        temp3 = lines[i + 2].strip().split()

                        temp1.append(0)
                        temp2.append(0)
                        temp3.append(0)

                        if len(temp1) != 5 or len(temp2) != 5 or len(temp3) != 5:
                            print(f"Error in lines {line_number}, {line_number + 1}, {line_number + 2}: Invalid number of elements in the line.")
                            flagSarva = 1

                        src1, des1, flit1 = temp1[1], temp1[2], temp1[3]
                        src2, des2, flit2 = temp2[1], temp2[2], temp2[3]
                        src3, des3, flit3 = temp3[1], temp3[2], temp3[3]

                        #Error handing if Source is Same as Destination
                        if src1 == des1 or src2 == des2 or src3 == des3:
                            print(f"Error in lines {line_number}, {line_number + 1}, {line_number + 2}: Source can't be the same as the destination.")
                            flagSarva = 1

                        #Error handing if Router Id is not given in range of 0 to 8
                        if (int(src1) not in range(0,9)) or (int(src2) not in range(0,9)) or (int(src3) not in range(0,9)) or (int(des1) not in range(0,9)) or (int(des2) not in range(0,9)) or(int(des3) not in range(0,9)):
                            print(f"Error in lines {line_number}, {line_number + 1}, {line_number + 2}: Invalid Router ID")
                            flagSarva = 1  

                        #Error handing if We don't have a valid flit
                        if (not is_valid_flit_type(flit1)) or (not is_valid_flit_type(flit2)) or (not is_valid_flit_type(flit3)):
                            print(f"Error in lines {line_number}, {line_number + 1}, {line_number + 2}: Invalid flit type.")
                            flagSarva = 1

                        #Error handing If mutiple flits of same type are given
                        if check_last_two_digits(temp1, temp2) or check_last_two_digits(temp2, temp3) or check_last_two_digits(temp1, temp3):
                            print(f"Error in lines {line_number}, {line_number + 1}, {line_number + 2}: Last two digits match.")
                            flagSarva = 1
                        
                        if flagSarva==1:
                            exit()

                        eachline2.extend([temp1, temp2, temp3])
                        line_number += 3

            except FileNotFoundError:
                print("Error: File 'traffic.txt' not found.")
            except Exception as e:
                print(f"An error occurred: {str(e)}")

            try:
                with open('delays.txt','r') as file1:
                    line1 = file1.readline()
                    line1 = line1.split()
                    mean_delays = [float(delay) for delay in line1]
                    line2 = []
                    delay_dic = {0 : 'Input Buffer' , 1 : 'Switch Allocator' , 2 : 'CrossBar' }
                    for i in range(0,len(line1)):
                        line2.append(float(line1[i]))
                        if line2[i] < 0:
                            print(f"Error : You have provided a negative value in delays file at {delay_dic[i]}")
                            exit()

            except FileNotFoundError:
                print("Error: File 'delays.txt' not found.")
                exit()
            except Exception as e:
                print(f"An error occurred: {str(e)}")
                exit()

            traffic_file = eachline2
            delay_file = line2

            buffer_delay = delay_file[0]
            sa_delay = delay_file[1]
            xbar_delay = delay_file[2]

            # print("Enter 0 to run in XY & 1 to run in YX ")
            # algo = int(input())
            # print("Enter 0 to run in PVA & 1 to run in PVS ")
            # run_mode = int(input())

            

            num_routers = 9
            buffer_delays = generate_gaussian_delays(mean_delays[0], mean_delays[0]*0.1, num_routers,run_mode)
            sa_delays = generate_gaussian_delays(mean_delays[1], mean_delays[1]*0.1, num_routers,run_mode)
            xbar_delays = generate_gaussian_delays(mean_delays[2], mean_delays[2]*0.1, num_routers,run_mode)

            all_routers = {i : Router(i,buffer_delays[i],sa_delays[i],xbar_delays[i]) for i in range(0,9)}
            
            #These line are here so that we can check how the delaysa being assigned
            for i in range(0,9):
                print(f"Router ID : {i} with BD = {all_routers[i].buffer_delay} : SA {all_routers[i].switch_allocator_delay} : XD : {all_routers[i].crossbar_delay}")
            # exit()

            print('\n')
            
            period = max(buffer_delay,sa_delay,xbar_delay)
            
            total = 0
            flit_time = []
            bubble_sort(traffic_file,len(traffic_file))

            clock_wise_flits = {} # keep a record what are flits to be added at a particular clock
            clock = 1

            links = {"01" : 0 ,"12" : 0 ,"03" : 0 ,"14" : 0 ,"25" : 0 ,"34" : 0 ,"45" : 0 ,"36" : 0 ,"47" : 0 ,"58" : 0 ,"67" : 0 ,"78" : 0 }
            received_flits = []
            delayed_list = []

            lastclock = int(traffic_file[len(traffic_file) - 1][0]) #last clock of injection 
            while(clock <= lastclock):
                flits_on_that_clock = []
                for i in range(0,len(traffic_file)):
                    if(int(traffic_file[i][0]) == clock): #this is clock of traffic file is injected on this particular clock cycle
                        flits_on_that_clock.append(traffic_file[i]) 
                if(flits_on_that_clock != []):
                    clock_wise_flits[clock] = flits_on_that_clock 
                clock += 1


            '''Logic :
                1. iterate on clock
                2. for each clock iterate on every router 
                3. if it is a clase of forward flow we will do it later in the second loop. For now we'll mark that router as pending.
                4. in case of backward flow it is done in the first loop itself 
                5. We have made injection as an independent process , we'll inject new flits when all the updatation is done (parallel injection enabled)
                '''
            
            clock = 1 #defining the clock
            while(clock <= lastclock or (not all_empty(all_routers))):
                pending=[]
    
                for i in all_routers:
                    curr_flit_details = all_routers[i].getflit()
                    
                    if(all_routers[i].isempty()):
                        pass
                    elif(len(all_routers[i].crossbar)!=0):
                        next_r = xy1(curr_flit_details,i) if (algo == 0) else yx1(curr_flit_details,i)
                        if(all_routers[i].is_destination_flit(curr_flit_details[2])):
                            all_routers[i].receive(period,received_flits,clock,delayed_list)
                        
                        elif(next_r>i):
                            pending.append(all_routers[i])
                        else:
                            all_routers[i].update(next_r,all_routers,period,links,clock,delayed_list)

                    else:
                        next_r = xy1(curr_flit_details,i) if (algo == 0) else yx1(curr_flit_details,i)
                        all_routers[i].update(next_r,all_routers,period,links,clock,delayed_list)


                for i in pending:
                    curr_flit_details = i.getflit()
                    next_r = xy1(curr_flit_details,i.router_id) if (algo == 0) else yx1(curr_flit_details,i.router_id)
                    i.update(next_r,all_routers,period,links,clock,delayed_list)


                if(clock in clock_wise_flits): # indicator that flit has to be injected in this cycle
                    flits_on_that_clock = clock_wise_flits[clock] #list of flits to be injected on this clock
                    
                    i = 8
                    while(i >= 0): #to update the the routers
                        r = all_routers[i] # Rth router
                        flits_on_this_router = [] #flits to be injected on this router on this cycle
                        for j in range(0,len(flits_on_that_clock)):
                            if(i == int(flits_on_that_clock[j][1])): # router_no == flit_src
                                flits_on_this_router.append(flits_on_that_clock[j])

                                                
                        while(len(flits_on_this_router) != 0):
                            r.inject(flits_on_this_router.pop(0))

                        i -=1 

                j = 0 
                while j <= 8:
                    try:
                        print(f"At clock cycle: {clock} = {all_routers[j]}")
                    except Exception as e:
                        print(f"Error printing router details: {str(e)} for value router no. = {j}")
                    j += 1

                print("---------------------------------------------------------------------------------------------------------\n")
                with open('Report.txt', 'a') as report_file:
                    for router_id, router in all_routers.items():
                        for stage, stage_name in enumerate(['input_buffer', 'switch_allocator', 'Crossbar']):
                            if not router.isempty() and len(getattr(router, stage_name.lower())) > 0:
                                flit_details = getattr(router, stage_name.lower())[0]
                                source = flit_details[1]
                                destination = flit_details[2]
                                delay = flit_details[4]
                                flit_type = decode_flit_type(flit_details[3])

                                report_file.write(f"At clock cycle: {clock}, Router ID: {router_id}, ")
                                report_file.write(f"The {flit_type} is traveling from Source {source} to destination {destination} at {stage_name} and its delay is {delay}.\n")
                                for delayed_item in delayed_list:
                                    if delayed_item[0] == clock and delayed_item[1] == router_id:
                                        delayed_flit = delayed_item[3]
                                        report_file.write(f"At clock cycle: {clock}, Router ID: {router_id}, ")
                                        report_file.write(f"The {flit_type} traveling from Source {source} to destination {destination} is being delayed at {decode_PE_type(delayed_item[2])}\n")

                    report_file.write("-----------------------------------------------------NEW CYCLE----------------------------------------------------\n")
                    report_file.write("\n")
                clock += 1
                total += period


                #emergency button
                if(clock == 40):
                    print("forcefull stop")
                    exit()

            formatted_links = {f"{key[0]}<-->{key[1]}": value for key, value in links.items()}   #dup dict just for desired graph axis
            pe_updates = {}
            for i in range(0,9):
                pe_updates[i] = all_routers[i].processing_element

            print(f"Clock frequency = {1/period}")
            print(f"Total Time = {(clock-1)*period}")


            print("\n")

            for flits in delayed_list:
                print(flits)

                 
    sys.stdout = sys.__stdout__

    print("Output is stored in a file name : 'Log_File.txt'")
    print("Report is Generated in a file named : 'Report.txt'")

    link_graph(formatted_links,pe_updates)
    graph2(traffic_file,received_flits)

except Exception as e:
    print(f"Error printing output location: {str(e)}")