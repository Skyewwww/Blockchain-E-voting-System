import json, time, random
from sys import argv
from threading import Thread
from peer import Peer
import socket
import wallet
import time

# check that a new vote has not already been made
def check_duplicate(new_vote, all_votes):
    all_votes_list = [json.loads(i) for i in all_votes]
    if new_vote is not None:
        all_votes_list.append(json.loads(new_vote))
    voters = [i['voter'] for i in all_votes_list]
    return len(voters) == len(set(voters))

# create syntax for a specific vote
def make_vote(voter, choice):
    return json.dumps({'voter': voter, 'choice': choice})

# return a dict of 'choice: votes'; assume no duplicates
def tally_votes(votes):
    all_votes_list = [json.loads(i) for i in votes]
    res = {}
    for vote in all_votes_list:
        if vote['choice'] in res:
            res[vote['choice']]  += 1
        else:
            res[vote['choice']] = 1
    return res



# voting machine class, provides distributed voting functionality
class VotingMachine:
    def __init__(self, self_addr, tracker_addr):
        self.node = Peer(self_addr=self_addr, tracker_addr=tracker_addr, data_crit=check_duplicate)
        self.is_mining = False
        self.voted = False

    def start(self):
        self.node.connect()

        # prompt user for input, whether they want to vote, view the tally, or quit. Handle accordingly
        while True:
            if self.voted:
                if self.isvalid():
                    print("***** OPTION LIST *****")
                    print("0: Create My Account")
                    print("1: View All Candidates")
                    print("2: Display Current Results")
                    print("3: Vote")
                    print("4: Display All Voting Records")
                    print("Q: Quit")
                    print("***********************")
                    op = str(input("Enter option: "))
                    if op == '0':
                        wallet.new_account()
                    elif op == '1':
                        print(self.node.candi_list)
                    elif op == '2':
                        print(tally_votes(self.node.get_data()))
                    elif op == '3':
                        if self.is_mining:
                            print("**Error: Please wait for current mining to finish...**")
                        else:
                            if not wallet.account_exist():
                                print("**Error: Please create your account before voting**")
                            else:
                                while True:
                                    voter = str(wallet.read_account())
                                    print("Voter:", voter)
                                    choice = int(input("Enter candidate number: "))
                                    candi_number = [candi['number'] for candi in self.node.candi_list]
                                    print(candi_number)
                                    if choice not in candi_number:
                                        print("**Error: Invaid candidate number!**")
                                    else:                            
                                        Thread(target=self.mining, args = (make_vote(voter, choice), )).start()
                                        break
                    elif op == '4':
                        if self.voted:
                            print(self.node.blockchain.display_chain())
                        else:
                            print("**Error: Please vote before viewing all records**")
                    elif op == 'q':
                        print("**Quitting**")
                        self.node.disconnect()
                        break
                    else:
                        print("Invalid option!")
                else:
                    print("**Error: Voting time is over!**")
                    max_result = max(tally_votes(self.node.get_data()),key=tally_votes(self.node.get_data()).get)
                    print(f"The winner is {max_result} !")
                    break
            else:
                print("***** OPTION LIST *****")
                print("0: Create My Account")
                print("1: View All Candidates")
                print("2: Display Current Results")
                print("3: Vote")
                print("4: Display All Voting Records")
                print("Q: Quit")
                print("***********************")
                op = str(input("Enter option: "))
                if op == '0':
                    wallet.new_account()
                elif op == '1':
                    print(self.node.candi_list)
                elif op == '2':
                    print(tally_votes(self.node.get_data()))
                elif op == '3':
                    if self.is_mining:
                        print("**Error: Please wait for current mining to finish...**")
                    else:
                        if not wallet.account_exist():
                            print("**Error: Please create your account before voting**")
                        else:
                            while True:
                                voter = str(wallet.read_account())
                                print("Voter:", voter)
                                choice = int(input("Enter candidate number: "))
                                candi_number = [candi['number'] for candi in self.node.candi_list]
                                print(candi_number)
                                if choice not in candi_number:
                                    print("**Error: Invaid candidate number!**")
                                else:                            
                                    Thread(target=self.mining, args = (make_vote(voter, choice), )).start()
                                    break
                elif op == '4':
                    if self.voted:
                        print(self.node.blockchain.display_chain())
                    else:
                        print("**Error: Please vote before viewing all records**")
                elif op == 'q':
                    print("**Quitting**")
                    self.node.disconnect()
                    break
                else:
                    print("Invalid option!")

    # mine to add to the blockchain  
    def mining(self, data):
        self.is_mining = True
        while True:
            res = self.node.add_data(data)
            if res == 1: 
                print("Vote is successfully added.\n")
                self.voted = True
                break
            elif res == 0:
                print("While mining, blockchain is changed. Retrying...\n")
                time.sleep(random.randint(0, 100) / 100.0 * 2.0)
            elif res == -1:
                print("Invalid/duplicate Vote!\n")
                break
        self.is_mining = False

    def isvalid(self):
        block = [block for block in self.node.blockchain.getchain()]
        gensis_block = block[0]
        start_time = int(gensis_block.timestamp)
        current_time = int(time.time())
        if (current_time - start_time) > 6000:
            return False
        else:
            return True


if __name__ == "__main__":
    self_host = socket.gethostname()
    self_port = int(argv[1])
    tracker_host = socket.gethostname()
    tracker_port = int(argv[2])
    VotingMachine(self_addr=(self_host, self_port), tracker_addr=(tracker_host, tracker_port)).start()

