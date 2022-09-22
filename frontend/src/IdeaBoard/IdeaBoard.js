import React from 'react';
import './IdeaBoard.css'

const IdeaBoard = props => {
  return (
    <div className="homepage-grid-container">
      {/* Card Components */}
      <div className="homepage_grid">
        <div className="item"></div>
        <div className="item"></div>
        <div className="item"></div>
        <div className="item"></div>
        <div className="item">
          {
            props.idea ? (
              <div className="center-idea">
                { props.idea.summary }
              </div>
            ) : (
              <input
                className="center-idea homepage-idea-input"
                onBlur={props.onIdeaSubmitted.bind(this)}
                onKeyDown={e => {
                  if (e.key === 'Enter') {
                    props.onIdeaSubmitted(e);
                  }
                }}
                placeholder="Type your idea here">
              </input>
            )
          }
        </div>
        <div className="item"></div>
        <div className="item"></div>
        <div className="item"></div>
        <div className="item"></div>
      </div>
    </div>
  )
}

export default IdeaBoard;