import React from 'react';
import { Type } from '../../Idea';
import { BubbleChild } from './BubbleChild';
import './styles.css';

export default class Bubble extends React.Component {
  constructor(props) {
    super(props);
    const data = this.props.data;
    this.state = {
      children: data.children,
      predictions: data.predictions,
      summary: data.summary,
      input: data.input,
      type: data.type,
    };
  }

  render() {
    return (
      <div className={`bubble ${this.state.type === Type.PREDICTIONS ? 'hasPredictions' : ''}`}
        onClick={this.props.onClick}
      >
        <div className="bubble-header">
            <h1 className="bubble-summary">
                {
                  this.state.type === Type.CHILDREN ?
                  this.state.summary :
                  (
                    this.state.type === Type.PREDICTIONS ?
                    (
                      <ol className="bubble-predictions">
                        {
                          this.state.summary.map((item, i) => {
                            return (
                              <li key={this.state.summary + 'pred' + i}>
                                { item }
                              </li>
                            );
                          })
                        }
                      </ol>
                    ) : ''
                  )
                }
            </h1>
        </div>
        <div className={`bubble-children ${this.state.children ? '' : 'no-children'}`}>
            {
              this.state.children &&
              this.state.children.filter(c => c.type === Type.CHILDREN).map((child, i) => {
                return <BubbleChild summary={child.summary} key={'bc' + i} />
              })
            }
        </div>
      </div>
    );
  }
}