const rewire = require("rewire")
const ab_actions = rewire("./ab_actions")
const AdminActions = ab_actions.__get__("AdminActions")
// @ponicode
describe("AdminActions", () => {
    test("0", () => {
        let callFunction = () => {
            AdminActions()
        }
    
        expect(callFunction).not.toThrow()
    })
})
