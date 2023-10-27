# Sample Hello World Beaker smart contract - the most basic starting point for an Algorand smart contract
import beaker as bk
import pyteal as pt
# from pyteal import Expr, Seq, Assert, Not
from beaker.lib.storage import BoxMapping
# from beaker.lib.storage import BoxList


class Mystate:
    result = bk.GlobalStateValue(pt.TealType.uint64)

class Proposal_Record(pt.abi.NamedTuple):
    proposal_id:pt.abi.Field[pt.abi.String]
    proposal_name:pt.abi.Field[pt.abi.String]
    asset_count:pt.abi.Field[pt.abi.Uint64]
    asset_id:pt.abi.Field[pt.abi.Uint64]
    Amount:pt.abi.Field[pt.abi.Uint64]
    # msg:pt.abi.Field[pt.abi.String]
    descr = "record stored"
    
class User_per_proposal_record(pt.abi.NamedTuple):
    user_id:pt.abi.Field[pt.abi.String]
    User_Token:pt.abi.Field[pt.abi.Uint64]

class Response_store(pt.abi.NamedTuple):
    response_id:pt.abi.Field[pt.abi.String]
    user_id:pt.abi.Field[pt.abi.String]
    User_Token:pt.abi.Field[pt.abi.Uint64]
    user_response:pt.abi.Field[pt.abi.Bool]



class Proposal_Record_State:
    proposal_rec = BoxMapping(pt.abi.String,Proposal_Record)
    user_rec = BoxMapping(pt.abi.String,User_per_proposal_record,prefix=pt.Bytes("_"))
    response_rec = BoxMapping(pt.abi.String,Response_store,prefix=pt.Bytes("@"))
    yes_count = bk.GlobalStateValue(
        stack_type=pt.TealType.uint64,
        default=pt.Int(0),
        descr="variable to store user response"
    )
    No_count = bk.GlobalStateValue(
        stack_type=pt.TealType.uint64,
        default=pt.Int(0),
        descr="variable to store user response"
    )
    user_res = bk.GlobalStateValue(
        stack_type=pt.TealType.uint64,
        default=pt.Int(0),
        descr="variable to store user response"
    )


app =(
     bk.Application("Voting_Proposal_Voting_EX",state = Proposal_Record_State())
     .apply(bk.unconditional_create_approval,initialize_global_state=True)
)



@app.external
def Register_proposal(proposal_id:pt.abi.String,proposal_name:pt.abi.String,asset_count:pt.abi.Uint64,asset_id:pt.abi.Uint64,Amount:pt.abi.Uint64,* ,output:Proposal_Record) -> pt.Expr:
    
    proposal_store = Proposal_Record()

  
    return pt.Seq(

        proposal_store.set(proposal_id,proposal_name,asset_count,asset_id,Amount),
        pt.Assert(app.state.proposal_rec[proposal_id.get()].exists()== pt.Int(0),comment="Proposal_ID already exists"),
        # output.set(pt.Concat(pt.Bytes("Proposal_id already exists, "))),
        app.state.proposal_rec[proposal_id.get()].set(proposal_store),
        # msg.set(pt.Concat(pt.Bytes("Proposal Registered Successfully "))),
        app.state.proposal_rec[proposal_id.get()].store_into(output),


    )

   
   
@app.external

def Registred_user_per_proposal(proposal_id:pt.abi.String,user_id:pt.abi.String,token_count:pt.abi.Uint64,*,output:User_per_proposal_record)-> pt.Expr:
    registred_user = User_per_proposal_record()
    proposal_get = Proposal_Record()

    return pt.Seq(
    proposal_get.decode(app.state.proposal_rec[proposal_id.get()].get()),
    registred_user.set(user_id,token_count),
    pt.Assert(app.state.user_rec[user_id.get()].exists()==pt.Int(0),comment="User_ID already exists"),
    app.state.user_rec[(user_id).get()].set(registred_user),
    app.state.user_rec[user_id.get()].store_into(output),
    )

@app.external

def update_proposal(proposal_id:pt.abi.String,proposal_name:pt.abi.String,asset_count:pt.abi.Uint64,asset_id:pt.abi.Uint64,Amount:pt.abi.Uint64,* ,output:Proposal_Record,)-> pt.Expr:
    existing_proposal_store = Proposal_Record()
    update_proposal_store = Proposal_Record()

    return pt.Seq(
        existing_proposal_store.decode(app.state.proposal_rec[proposal_id.get()].get()),
        update_proposal_store.set(proposal_id,proposal_name,asset_count,asset_id,Amount),
        app.state.proposal_rec[proposal_id.get()].set(update_proposal_store),
        app.state.proposal_rec[proposal_id.get()].store_into(output),
       


    )

@app.external
def Update_Users(proposal_id:pt.abi.String,user_id:pt.abi.String,token_count:pt.abi.Uint64,*,output:User_per_proposal_record)->pt.Expr:
    existing_user_store = User_per_proposal_record()
    update_user_store = User_per_proposal_record()
    proposal_get = Proposal_Record()
    return pt.Seq(
        proposal_get.decode(app.state.proposal_rec[proposal_id.get()].get()),
        existing_user_store.decode(app.state.user_rec[user_id.get()].get()),
        update_user_store.set(user_id,token_count),
        app.state.user_rec[user_id.get()].set(update_user_store),
        app.state.user_rec[user_id.get()].store_into(output),


    )

@app.external
def Voting_Record(proposal_id:pt.abi.String,response_id:pt.abi.String,user_id:pt.abi.String,token_count:pt.abi.Uint64,user_response:pt.abi.Bool,*,output:Response_store)-> pt.Expr:
    proposal_get = Proposal_Record()
    user_store = User_per_proposal_record()
    response_get = Response_store()

    return pt.Seq(
        # Validating user_id and proposal_id to ensure data integrity.
        proposal_get.decode(app.state.proposal_rec[proposal_id.get()].get()),
        user_store.decode(app.state.user_rec[user_id.get()].get()),
        # here we have created a additional functionality user can input the token_count for the voting weightage.
        # He can input the amout on tocken count he want to use for voting.
        # response_get.set(response_id,user_id,token_count),
        response_get.set(response_id,user_id,token_count,user_response),
        app.state.response_rec[user_id.get()].set(response_get),
        app.state.response_rec[user_id.get()].store_into(output),
        pt.If (user_response.get()== 1).Then(
            app.state.yes_count.increment(token_count.get())
            ).Else(
            app.state.No_count.increment(token_count.get())
        ),
        # app.state.yes_count.increment(token_count.get()),
        # app.state.No_count.increment(token_count.get())

    )

@app.external
def Result(proposal_id:pt.abi.String,*,output:pt.abi.String)-> pt.Expr:
    proposal_get = Proposal_Record()
    # response_get = Response_store()
    
    


    return pt.Seq(
    proposal_get.decode(app.state.proposal_rec[proposal_id.get()].get()),
    # response_get.decode(app.state.response_rec[user_id.get()].get()),
    # output.set(pt.Concat(pt.Bytes("Result "),response_get.load()))

    )

    

@app.external

def read_proposal_store(proposal_id:pt.abi.String,*,output:Proposal_Record)-> pt.Expr:
    return app.state.proposal_rec[proposal_id.get()].store_into(output)

@app.external

def read_user_proposal_store(user_id:pt.abi.String,*,output:User_per_proposal_record)-> pt.Expr:
    return app.state.user_rec[user_id.get()].store_into(output)

@app.external

def read_user_response(user_id:pt.abi.String,*,output:Response_store)-> pt.Expr:
    return app.state.response_rec[user_id.get()].store_into(output)


if __name__=="__main__":
    
    spec=app.build()
    
    spec.export("artifacts")



