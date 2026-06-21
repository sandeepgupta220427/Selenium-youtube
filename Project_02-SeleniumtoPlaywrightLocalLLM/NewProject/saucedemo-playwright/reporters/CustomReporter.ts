import { FullConfig, FullResult, Reporter, Suite, TestCase, TestResult } from '@playwright/test/reporter';

class CustomReporter implements Reporter {
    onBegin(config: FullConfig, suite: Suite) {
        console.log(`\n🚀 Starting the test run with ${suite.allTests().length} tests`);
    }

    onTestBegin(test: TestCase) {
        console.log(`\n▶️ Starting test: ${test.title}`);
    }

    onStepBegin(test: TestCase, result: TestResult, step: any) {
        if (step.category === 'test.step') {
            console.log(`   🔸 Step: ${step.title}`);
        }
    }

    onTestEnd(test: TestCase, result: TestResult) {
        const statusIcon = result.status === 'passed' ? '✅' : '❌';
        console.log(`${statusIcon} Finished test ${test.title}: ${result.status.toUpperCase()}`);
    }

    async onEnd(result: FullResult) {
        console.log(`\n🏁 Test run finished with status: ${result.status.toUpperCase()}\n`);
    }
}

export default CustomReporter;
