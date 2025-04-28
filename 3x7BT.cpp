

#include <iostream>
#include <vector>
#include <string>
#include <unordered_set>

using namespace std;


class State{
public:
    vector<vector<int>> board;
    bool wTurn;

    State(){
        for (int i = 0; i<6; i++){
            vector<int> tmp = {};
            for (int k = 0; k < 3; k++){
                if (i <= 1) {tmp.push_back(2);}
                else if (i <= 3) {tmp.push_back(0);}
                else {tmp.push_back(1);}
            }
            this->board.push_back(tmp);
        }
        this->wTurn = true;
    }

    vector<vector<vector<int>>> actions(){
        vector<vector<vector<int>>> states = {};
        if (this->wTurn){
            for (int i = 0; i < 6; i++){
                for( int k = 0; k < 3; k++){
                    if (this->board[i][k] == 1){
                        //left capture
                        if (k == 1 || k == 2){
                            if (this->board[i-1][k-1] == 2){
                                //change board and append new state then unchange
                                vector<vector<int>> newBoard = this->board;
                                newBoard[i][k] = 0;
                                newBoard[i-1][k-1] = 1;
                                states.push_back(newBoard);
                            }
                        }
                        //right capture
                        if (k == 0 || k == 1){
                            if(this->board[i-1][k+1] == 2){
                                //change board and append new state then unchange
                                vector<vector<int>> newBoard = this->board;
                                newBoard[i][k] = 0;
                                newBoard[i-1][k+1] = 1;
                                states.push_back(newBoard);
                            }
                        }
                        //move forward
                        if(k == 0 || k == 1 || k == 2){ //redundant check 
                            if(this->board[i-1][k] == 0){
                                //change board and append new state then unchange
                                vector<vector<int>> newBoard = this->board;
                                newBoard[i][k] = 0;
                                newBoard[i-1][k+1] = 1;
                                states.push_back(newBoard);
                            }
                        }
                    }
                }
            }
        }else{
            for (int i = 0; i < 6; i++){
                for( int k = 0; k < 3; k++){
                    if (this->board[i][k] == 2){
                        //left capture
                        if (k == 1 || k == 2){
                            if (this->board[i+1][k-1] == 1){
                                //change board and append new state then unchange
                                vector<vector<int>> newBoard = this->board;
                                newBoard[i][k] = 0;
                                newBoard[i+1][k-1] = 2;
                                states.push_back(newBoard);
                            }
                        }
                        //right capture
                        if (k == 0 || k == 1){
                            if(this->board[i+1][k+1] == 1){
                                //change board and append new state then unchange
                                vector<vector<int>> newBoard = this->board;
                                newBoard[i][k] = 0;
                                newBoard[i+1][k+1] = 2;
                                states.push_back(newBoard);
                            }
                        }
                        //move forward
                        if(k == 0 || k == 1 || k == 2){ //redundant check 
                            if(this->board[i+1][k] == 0){
                                //change board and append new state then unchange
                                vector<vector<int>> newBoard = this->board;
                                newBoard[i][k] = 0;
                                newBoard[i+1][k] = 2;
                                states.push_back(newBoard);
                            }
                        }
                    }
                }
            }
        }
        return states;
    }

    void make(vector<vector<int>> boardState){
        this->board = boardState;
        this->wTurn = !this->wTurn;
    }

    bool isTerminal(){
        if (this->board[0][0] == 1 || this->board[0][1] == 1 || this->board[0][2] == 1) return true;
        if (this->board[5][0] == 2 || this->board[5][1] == 2 || this->board[5][2] == 2) return true;
        if(this->actions().size() == 0) return true;
        return false;
    }

    void printBoard(){
        for (int i = 0; i<6; i++){
            for (int k = 0; k < 3; k++) cout << this->board[i][k] << " ";
            cout << endl;
        }
    }

    string boardString(){
        string ret = "";
        for(int i = 0; i < 6; i++){
            for(int k = 0; k < 3; k++) ret += to_string(this->board[i][k]);
        }
        return ret + to_string(this->wTurn);
    }

};

unordered_set<string> visited;
int totalTerminalstates = 0;
int totalNonTerminalstates = 0;

void dfs_recur(State state){
    if (state.isTerminal()){
        state.printBoard();
        cout << state.wTurn << endl;
        cout << endl;
        totalTerminalstates++;
        return;
    }else{
        totalNonTerminalstates++;
    }
    if (visited.count(state.boardString()) > 0) {
        return;
    }
    visited.insert(state.boardString());

    vector<vector<vector<int>>> actions = state.actions();

    for (int i = 0; i < actions.size(); i++){
        vector<vector<int>> tmp = state.board;
        bool turn = state.wTurn;
        state.make(actions[i]);
        dfs_recur(state);
        state.board = tmp;
        state.wTurn = turn;
    }

}

void dfs(State state){

    visited.clear();
    dfs_recur(state);
    cout << "total terminal states: " << totalTerminalstates << endl;
    cout << "total non-terminal states: " << totalNonTerminalstates << endl;

}

int main() {
    
    State state = State();
    dfs(state);
    return 0;
}

