import React, { Component } from "react";
import {
    Form,
    Row,
    Col,
    Button,
    Spinner
  } from "react-bootstrap";
  import * as icon from "react-icons/all";
import { IconContext } from "react-icons";
import "./NetworkTable.scss";
export default class SubnetTable extends Component {
constructor(props){
super();
console.log("SubnetLoading",props);
this.state = {
  Subnet:props.Subnet.subnet_name,
  VMS:props.VMS,
  nw_name:props.NetworkName,
    expanded: false }
}

toggleExpander = (e) => {
    if (!this.state.expanded) {
      this.setState(
        { expanded: true }
      )
    } else {
     this.setState({ expanded: false }); 
    }
  }


render(){
    return(
        <tbody  className="Subnet">
            <tr onClick={this.toggleExpander}  className="SubnetRow tData">
            <td >{ this.state.expanded ? <IconContext.Provider value={{ color: "#1DA1F2" }}>
  <div>
  <icon.BsCaretDownFill  /> 
  </div>
</IconContext.Provider> :  <icon.BsCaretRightFill /> } 
           </td>
    <td>{this.props.Subnet.subnet_name}</td>
    <td>{this.props.Subnet.cidr}</td>
    <td>{this.props.Subnet.subnet_type}</td>
    <td onClick={()=>this.props.DeleteSubnet(this.state.Subnet,this.state.nw_name)}>
            <svg
              width="1em"
              id="Del"
              height="1em"
              viewBox="0 0 16 16"
              className="bi bi-trash-fill"
              fill="currentColor"
              xmlns="http://www.w3.org/2000/svg"
            >
              <path
                id="Del"
                fillRule="evenodd"
                d="M2.5 1a1 1 0 0 0-1 1v1a1 1 0 0 0 1 1H3v9a2 2 0 0 0 2 2h6a2 2 0 0 0 2-2V4h.5a1 1 0 0 0 1-1V2a1 1 0 0 0-1-1H10a1 1 0 0 0-1-1H7a1 1 0 0 0-1 1H2.5zm3 4a.5.5 0 0 1 .5.5v7a.5.5 0 0 1-1 0v-7a.5.5 0 0 1 .5-.5zM8 5a.5.5 0 0 1 .5.5v7a.5.5 0 0 1-1 0v-7A.5.5 0 0 1 8 5zm3 .5a.5.5 0 0 0-1 0v7a.5.5 0 0 0 1 0v-7z"
              />
            </svg>
          </td>
          <td></td>
            </tr>
            {
            this.state.expanded && (
                <tr className="expandable " key="tr-expander"  onDrop={(e)=>this.props.drop(e,this.state.Subnet,this.state.nw_name)} onDragOver={(e)=>this.props.allowDrop(e)}>
                    <td className="uk-background-muted" colSpan={6}>
                    <Row className="font-weight-bold py-3 ml-1  ">
                              
                              <Col className="rdColCenter" xs={{ span: 2 }}>HOST NAME</Col>
                              <Col  className="rdColCenter" xs={{ span: 2 }}>IP</Col>
                              <Col className="rdColCenter" xs={{ span: 2 }}>MACHINE TYPE</Col>
                              <Col className="rdColCenter" xs={{ span: 4 }}>ACTION</Col>
                               <Col className="rdColCenter" xs={{ span: 1 }}>STATUS</Col> 
                            </Row>
                            {this.props.Subnet.hosts === undefined || this.props.Subnet.hosts.length === 0  ? (
                  <h6 className="text-center text-muted">
                       No SubnetData Avaialble...
                       </h6>
                  ) : (
                    this.props.Subnet.hosts.map((host, index) => (
                      <Row className=" py-3 HostRow" key={index} id={host.hostname} draggable={true} onDragStart={(e)=>this.props.drag(e,host,index,this.state.Subnet,this.state.nw_name)}>
                    
                       <Col className="rdColCenter txts" xs={{ span: 2 }}>{host.hostname}</Col>
                      <Col className="rdColCenter txts" xs={{ span: 2 }}>{host.ip}</Col> 
                      <Col className="rdColCenter"  xs={{ span: 2 }}>
                        <Form>
                          <Form.Group controlId="select-machine-type">
                            <Form.Control
                              className="select-blueprint-edit"
                              defaultValue={host.machine_type}
                              as="select"
                              size="sm"
                              onChange={(e)=>this.props.handleVM(e,host)}
                            >
                     {this.state.VMS.map((VM) => (
                  <option key={VM.vm_name} value={VM.vm_name}>
                    {VM.vm_name}
                  </option>
                ))}
                            </Form.Control>
                          </Form.Group>
                        </Form> 
                      </Col>
                      <Col className="rdColCenter" xs={{ span: 4 }}>   
                      <Button
                      className=" media-body"
                      variant="info"
                      size="sm"
                      disabled={host["BtStatus"] !=="prepare" || host["BtProgress"] === "prepareStarted" || host["BtProgress"] === "cloneStarted"}
                      onClick={()=>this.props.BlueprintHostPrepare(host.hostname)}
                    >
                      {
                         host["BtProgress"] === "prepareStarted" ? <><Spinner as="span" animation="grow" size="sm" role="status"  aria-hidden="true"/> In Progess...</> : <> Prepare</>
                      }
                      
                    </Button>
                 ----
                       <Button
                      className=" media-body"
                      variant="success"
                      size="sm"
                      disabled={(host["BtStatus"] !=="clone" && host["BtStatus"] !=="prepare" )|| host["BtProgress"] === "cloneStarted"}
                      onClick={()=>this.props.BlueprintHostClone(host.hostname)}
                    >
                      {
                         host["BtProgress"] === "cloneStarted" ? <><Spinner as="span" animation="grow" size="sm" role="status"  aria-hidden="true"/> In Progess...</> : <> Clone</>
                      }
                      
                    </Button>
                   ----
                                   <Button
                      className=" media-body"
                      variant="danger"
                      size="sm"
                      disabled={host["BtStatus"] !=="convert" || host["BtProgress"] === "convertStarted"}
                      onClick={()=>this.props.BlueprintHostConvert(host.hostname)}
                    >
                     {
                         host["BtProgress"] === "convertStarted" ? <><Spinner as="span" animation="grow" size="sm" role="status"  aria-hidden="true"/> In Progess...</> : <> Convert</>
                      }
                    </Button>
                    ----
                    <Button
                      className=" media-body"
                      variant="primary"
                      size="sm"
                      disabled={host["BtStatus"] !== "build" || host["BtProgress"] === "buildStarted"}
                      onClick={()=>this.props.BlueprintHostBuild(host.hostname)}
                    >
                      {
                         host["BtProgress"] === "buildStarted" ? <><Spinner as="span" animation="grow" size="sm" role="status"  aria-hidden="true"/> In Progess...</> : <> Build</>
                      }
                    </Button></Col>
                     <Col className="rdColCenter" xs={{ span: 1 }}>{host.status}</Col> 
                    </Row>
               
                    ))
                  )}
                            
                    </td>
                </tr>
            )}
        </tbody>
    )
}
}